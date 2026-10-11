"""Parser for dashboard plans, plan format v2 (see references/plan-format.md).

Shared by the planner and executor skills. The copies must stay identical;
the repo's tools/sync_plan_format.py copies this file to every executor.
"""
import re

PLAN_VERSION = 2
GOALS = {"answer", "spec", "explore", "monitor", "present"}
AUDIENCES = {"me", "team", "leadership", "clients"}
ENUMS = {
    "cadence": {"one-time", "daily", "weekly", "monthly"},
    "review_depth": {"quick", "guided", "deep"},
    "destination": {"local", "artifact", "dashboard-type", "self-hosted"},
}
SECTIONS = ["Assumptions", "Data", "Story", "Interaction", "Style", "Data for the executor"]
FORMS = {
    "trend": ({"x", "y"}, {"brush", "none"}),
    "bar": ({"category", "value"}, {"click", "none"}),
    "histogram": ({"value"}, {"brush", "none"}),
    "scatter": ({"x", "y"}, {"brush", "none"}),
    "exceptions": ({"category", "value"}, {"none"}),
}
# Chart keys that hold settings, not column names.
SETTING_KEYS = {"from", "above", "below", "format"}
FORMATS = {"number", "compact", "percent", "currency"}
BUCKETS = {"day", "week", "month", "quarter", "year"}
VALUE_RE = re.compile(r"^(count|sum|avg|median|min|max|rate)\((.*)\)$")
NUMBER_RE = re.compile(r"^-?\d+(?:\.\d+)?%?$")


def parse_value(expr):
    """'sum(revenue)' -> ('sum', 'revenue'); 'count()' -> ('count', None). Raises ValueError."""
    m = VALUE_RE.match(expr.strip())
    if not m:
        raise ValueError(f"'{expr}' is not a value expression like sum(col), count(), rate(col)")
    agg, col = m.group(1), m.group(2).strip() or None
    if agg != "count" and not col:
        raise ValueError(f"'{expr}' needs a column, e.g. {agg}(amount)")
    return agg, col


def parse_number(text):
    """'0.08' -> 0.08, '8%' -> 0.08. Raises ValueError."""
    text = str(text).strip()
    if not NUMBER_RE.match(text):
        raise ValueError(f"'{text}' is not a number like 1200, 0.08 or 8%")
    return float(text[:-1]) / 100 if text.endswith("%") else float(text)


def as_list(value):
    """Header lists may be written 'a, b' or as a YAML list."""
    if value is None:
        return []
    items = value if isinstance(value, list) else str(value).split(",")
    return [str(v).strip().lower() for v in items if str(v).strip()]


def _header(text):
    m = re.match(r"^---\s*\n(.*?)\n---\s*\n", text, re.DOTALL)
    if not m:
        return None, text
    raw, body = m.group(1), text[m.end():]
    try:
        import yaml
        return yaml.safe_load(raw) or {}, body
    except ImportError:
        pass
    # Minimal fallback for the header shape this format uses.
    head, current = {}, None
    for line in raw.splitlines():
        if not line.strip() or line.strip().startswith("#"):
            continue
        item = re.match(r"^\s*-\s*(\w+):\s*(.*)$", line)
        sub = re.match(r"^\s+(\w+):\s*(.*)$", line)
        top = re.match(r"^(\w+):\s*(.*)$", line)
        if item and current is not None:
            current.append({item.group(1): _scalar(item.group(2))})
        elif sub and current:
            current[-1][sub.group(1)] = _scalar(sub.group(2))
        elif top:
            key, val = top.group(1), top.group(2).split(" #")[0].strip()
            if val:
                head[key], current = _scalar(val), None
            else:
                head[key] = current = []
    return head, body


def _scalar(v):
    v = v.split(" #")[0].strip()
    if len(v) >= 2 and v[0] == v[-1] and v[0] in "\"'":
        return v[1:-1]
    if v.lower() in ("true", "false"):
        return v.lower() == "true"
    return int(v) if re.fullmatch(r"\d+", v) else v


def parse(text):
    """Return (plan dict, list of format errors). Never raises on bad input."""
    errors = []
    head, body = _header(text)
    if head is None:
        return {}, ["Missing YAML header between --- lines at the top of the plan"]

    plan = {"header": head, "kpis": [], "charts": [], "menus": [], "style": {}, "sql": []}
    version = head.get("plan_version")
    if version == 1:
        errors.append("plan_version 1 is no longer supported. Re-run the planner, or update the header to v2: "
                      "replace persona and mode with goals, audience, cadence, review_depth, success_criteria "
                      "and reconcile (see the planner's references/plan-format.md)")
    elif version != PLAN_VERSION:
        errors.append(f"plan_version: got {version!r}, expected {PLAN_VERSION}")
    _intent(head, plan, errors)
    files = head.get("data") or []
    if not isinstance(files, list) or not all(isinstance(f, dict) and f.get("file") for f in files):
        errors.append("data: list each executor file as '- file: name' with 'rows: N'")
        files = []
    plan["files"] = files

    title = re.search(r"^#\s+(.+)$", body, re.MULTILINE)
    if not title:
        errors.append("Missing '# Title' line after the header")
    plan["title"] = title.group(1).strip() if title else ""
    first_section = re.search(r"^##\s", body, re.MULTILINE)
    intro = body[title.end():first_section.start()] if title and first_section else ""
    plan["takeaway"] = " ".join(intro.split())

    sections, current = {}, None
    for line in body.splitlines():
        m = re.match(r"^##\s+(.+?)\s*$", line)
        if m:
            current = m.group(1)
            sections[current] = []
        elif current:
            sections[current].append(line)
    sections = {k: "\n".join(v).strip() for k, v in sections.items()}
    plan["sections"] = sections
    for s in SECTIONS:
        if s not in sections:
            errors.append(f"Missing section '## {s}'")

    _story(sections.get("Story", ""), plan, errors)

    inter = sections.get("Interaction", "")
    menus = re.search(r"Menus:\s*(.+)", inter)
    if menus and menus.group(1).strip().lower() != "none":
        plan["menus"] = [c.strip() for c in menus.group(1).split(",") if c.strip()]
    for key, name in (("detail_table", "Detail table"), ("sql_on_page", "SQL on page")):
        m = re.search(rf"{name}:\s*(yes|no)", inter, re.IGNORECASE)
        if not m:
            errors.append(f"Interaction: add '- {name}: yes' or '- {name}: no'")
        plan[key] = bool(m and m.group(1).lower() == "yes")
    updated = re.search(r"Last updated:\s*(\S+)", inter)
    plan["last_updated"] = updated.group(1) if updated and updated.group(1).lower() != "none" else None

    for m in re.finditer(r"^\s*-\s*(\w+):\s*(\S+)", sections.get("Style", ""), re.MULTILINE):
        plan["style"][m.group(1).lower()] = m.group(2)
    for key in ("accent", "alert"):
        if key in plan["style"] and not re.fullmatch(r"#[0-9a-fA-F]{6}", plan["style"][key]):
            errors.append(f"Style: {key} must be a #rrggbb color, got {plan['style'][key]}")

    plan["sql"] = [s.strip() for s in re.findall(r"```sql\s*(.*?)```", sections.get("Data for the executor", ""), re.DOTALL)]
    if not plan["sql"]:
        errors.append("Data for the executor: add the SQL that produced each data file in a ```sql block")
    return plan, errors


def _intent(head, plan, errors):
    """Header fields from intake: goals, audience, cadence, review_depth, success_criteria, reconcile, comparison_period."""
    goals = as_list(head.get("goals"))
    if not 1 <= len(goals) <= 2 or any(g not in GOALS for g in goals):
        errors.append(f"goals: got {head.get('goals')!r}, expected one or two of {sorted(GOALS)}, e.g. 'goals: answer, present'")
    plan["goals"] = goals
    audience = as_list(head.get("audience"))
    if not audience or any(a not in AUDIENCES for a in audience):
        errors.append(f"audience: got {head.get('audience')!r}, expected one or more of {sorted(AUDIENCES)}")
    plan["audience"] = audience
    for key, allowed in ENUMS.items():
        val = str(head.get(key, "")).strip().lower()
        if val not in allowed:
            errors.append(f"{key}: got {head.get(key)!r}, expected one of {sorted(allowed)}")
        plan[key] = val
    criteria = str(head.get("success_criteria") or "").strip()
    if not criteria:
        errors.append("success_criteria: add what makes this dashboard useful, or 'none stated'")
    plan["success_criteria"] = "" if criteria.lower() == "none stated" else criteria
    reconcile = head.get("reconcile")
    if not isinstance(reconcile, bool):
        errors.append(f"reconcile: got {reconcile!r}, expected true or false")
    plan["reconcile"] = reconcile is True
    plan["comparison"] = None
    comp = head.get("comparison_period")
    if comp and str(comp).strip().lower() != "none":
        col, _, bucket = str(comp).strip().partition(":")
        if not col or bucket not in BUCKETS:
            errors.append(f"comparison_period: got {comp!r}, expected <date column>:<{' | '.join(sorted(BUCKETS))}>, e.g. order_date:week")
        else:
            plan["comparison"] = {"column": col, "bucket": bucket}


def _kpis(text, plan, errors):
    for part in [p.strip() for p in text.split(";") if p.strip()]:
        m = re.match(r"^(.+?)\s*=\s*(.+?)\s*(?:\[(\w+)\])?\s*(?:target\s*(<=|>=)\s*(\S+))?$", part)
        if not m:
            errors.append(f"Story: KPI '{part}' should look like 'Label = sum(col) [format]' or '... [format] target>=100'")
            continue
        label, value, fmt = m.group(1), m.group(2), (m.group(3) or "number")
        try:
            parse_value(value)
        except ValueError as e:
            errors.append(f"Story: KPI {label}: {e}")
        if fmt not in FORMATS:
            errors.append(f"Story: KPI {label}: format [{fmt}] must be one of {sorted(FORMATS)}")
        kpi = {"label": label, "value": value, "format": fmt}
        if m.group(4):
            try:
                kpi["target"] = {"op": m.group(4), "value": parse_number(m.group(5))}
            except ValueError as e:
                errors.append(f"Story: KPI {label}: target {e}")
        plan["kpis"].append(kpi)


def _story(story, plan, errors):
    chart = None
    for line in story.splitlines():
        stripped = line.strip()
        if chart and stripped.startswith(">"):
            chart["note"] = " ".join(filter(None, [chart["note"], stripped[1:].strip()]))
            continue
        if chart and stripped.startswith("@"):
            at, sep, label = stripped[1:].partition(":")
            if not sep or not at.strip() or not label.strip():
                errors.append(f'Story: "{chart["title"]}": annotation should look like "@ 2025-03-01: Price change": {stripped}')
            else:
                chart["annotations"].append({"at": at.strip(), "label": label.strip()})
            continue
        kpi = re.match(r"^\s*\d+\.\s*KPIs:\s*(.+)$", line)
        if kpi:
            chart = None
            _kpis(kpi.group(1), plan, errors)
            continue
        m = re.match(r'^\s*\d+\.\s*"(.+?)"\s*\|\s*(\w+)\s*\|\s*([^|]*)\|\s*(\w+)\s*$', line)
        if not m:
            if re.match(r"^\s*\d+\.", line):
                errors.append(f'Story: line not in the format 2. "Title" | form | key=value ... | interaction: {stripped}')
            chart = None
            continue
        title, form, keys_raw, inter = m.groups()
        keys = dict(re.findall(r"(\w+)=(\S+)", keys_raw))
        chart = {"title": title, "form": form, "keys": keys, "interaction": inter, "note": "", "annotations": []}
        plan["charts"].append(chart)
        if form not in FORMS:
            errors.append(f'Story: "{title}": form {form!r} must be one of {sorted(FORMS)}')
            continue
        required, interactions = FORMS[form]
        missing = required - keys.keys()
        if missing:
            errors.append(f'Story: "{title}": {form} needs {", ".join(sorted(missing))}')
        if inter not in interactions:
            errors.append(f'Story: "{title}": {form} interaction must be one of {sorted(interactions)}')
        if form == "trend" and "x" in keys:
            col, _, bucket = keys["x"].partition(":")
            if bucket not in BUCKETS:
                errors.append(f'Story: "{title}": x needs a bucket, e.g. x={col}:week')
        for key in ("y", "value") if form in ("trend", "bar", "exceptions") else ():
            if key in keys:
                try:
                    parse_value(keys[key])
                except ValueError as e:
                    errors.append(f'Story: "{title}": {e}')
        if form == "exceptions":
            limits = [k for k in ("above", "below") if k in keys]
            if len(limits) != 1:
                errors.append(f'Story: "{title}": exceptions needs exactly one of above=<number> or below=<number>')
            for k in limits:
                try:
                    keys[k] = parse_number(keys[k])
                except ValueError as e:
                    errors.append(f'Story: "{title}": {k} {e}')
        if keys.get("format", "number") not in FORMATS:
            errors.append(f'Story: "{title}": format must be one of {sorted(FORMATS)}')
    if not plan["kpis"]:
        errors.append("Story: first line must be '1. KPIs: Label = value [format]; ...'")
    if not plan["charts"]:
        errors.append('Story: add at least one chart line, e.g. 2. "Orders peaked in May" | trend | x=date:week y=count() | brush')


def columns_used(plan):
    """Yield (data file or None for default, column, where) for every column the plan references."""
    for k in plan["kpis"]:
        try:
            _, col = parse_value(k["value"])
        except ValueError:
            continue
        if col:
            yield None, col, f"KPI {k['label']}"
    for c in plan["charts"]:
        src, keys, where = c["keys"].get("from"), c["keys"], f'"{c["title"]}"'
        for key, val in keys.items():
            if key in SETTING_KEYS:
                continue
            if VALUE_RE.match(val):
                col = parse_value(val)[1]
            else:
                col = val.partition(":")[0]
            if col:
                yield src, col, where
    for m in plan["menus"]:
        yield None, m, "Menus"
    if plan.get("comparison"):
        yield None, plan["comparison"]["column"], "comparison_period"
    if plan.get("last_updated"):
        yield None, plan["last_updated"], "Last updated"
