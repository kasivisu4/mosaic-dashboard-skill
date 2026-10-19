"""Validate a dashboard plan before handing it to an executor.

Usage: python validate_plan.py <plan.md>

Checks the plan against references/plan-format.md, the goal, audience and cadence
rules (guidelines/goals.md), that every
data file exists with the stated row count, that every column the plan uses
exists in its data file, and that every SQL block runs.
Paths in the plan are relative to the plan's folder.
Exit code 0 = OK (warnings allowed), 1 = errors to fix.
"""
import os
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plan_format import as_list, columns_used, parse  # noqa: E402

try:
    import duckdb
except ImportError:
    sys.exit("duckdb is not installed. Run: pip install duckdb")

# Audience hard limits, from references/style-system.md (Audience overrides). With several
# audiences, the strictest one wins. Orders: low -> high.
AUDIENCE_LIMITS = {
    "me":         {"kpis": 8, "sql": True,  "density": "dense",    "interaction": "full",  "motion": "reveal",      "provenance": "hidden",     "type_scale": "compact"},
    "team":       {"kpis": 6, "sql": True,  "density": "dense",    "interaction": "full",  "motion": "reveal",      "provenance": "hidden",     "type_scale": "compact"},
    "leadership": {"kpis": 5, "sql": False, "density": "balanced", "interaction": "light", "motion": "reveal",      "provenance": "footnote",   "type_scale": "standard"},
    "clients":    {"kpis": 4, "sql": False, "density": "balanced", "interaction": "light", "motion": "reveal",      "provenance": "footnote",   "type_scale": "standard"},
    "regulators": {"kpis": 4, "sql": False, "density": "balanced", "interaction": "light", "motion": "none",        "provenance": "per-number", "type_scale": "standard"},
}
ORDER = {
    "density": ["sparse", "balanced", "dense"],
    "interaction": ["none", "light", "full"],
    "motion": ["none", "transitions", "reveal"],
    "provenance": ["hidden", "footnote", "inline", "per-number"],
    "type_scale": ["compact", "standard", "display"],
}
# Chart forms each audience may not use (style-system.md, Audience overrides).
AUDIENCE_BANNED_FORMS = {"leadership": {"scatter"}, "clients": {"scatter", "histogram"}, "regulators": {"scatter"}}
# First-screen caps per density (style-system.md, Density caps): (KPI tiles, charts).
DENSITY_CAPS = {"sparse": (4, 3), "balanced": (5, 6), "dense": (8, 12)}
# Daily pages are glanceable: past this many charts they stop being a quick check.
MAX_DAILY_CHARTS = 4
# A stage below this many scenes is a grid; above, readers lose the thread (references/stage.md).
MIN_SCENES, MAX_SCENES = 6, 12


def sql_str(path):
    return "'" + str(path).replace("'", "''") + "'"


def goal_rules(plan, errors, warnings):
    """Rules that follow from the intake fields (see guidelines/goals.md)."""
    goals, audience, cadence = plan["goals"], plan["audience"], plan["cadence"]
    limits = [(a, AUDIENCE_LIMITS[a]) for a in audience if a in AUDIENCE_LIMITS]
    no_sql = [a for a, lim in limits if not lim["sql"]]
    if no_sql and plan["sql_on_page"]:
        errors.append(f"Interaction: pages for {', '.join(no_sql)} use 'SQL on page: no'")
    if limits:
        who, cap = min(((a, lim["kpis"]) for a, lim in limits), key=lambda x: x[1])
        if len(plan["kpis"]) > cap:
            errors.append(f"Story: pages for {who} have at most {cap} KPIs, found {len(plan['kpis'])}")
    if "regulators" in audience and not plan["reconcile"]:
        errors.append("reconcile: pages for regulators always reconcile, so use 'reconcile: true'")
    # Audience limits are hard (style-system.md): below 'full' interaction there is no detail table.
    table_allowed = all(lim["interaction"] == "full" for _, lim in limits)
    if ("explore" in goals or plan["review_depth"] == "deep") and table_allowed and not plan["detail_table"]:
        errors.append("Interaction: explore goals and deep review use 'Detail table: yes'")
    if plan["detail_table"] and not table_allowed:
        capped = [a for a, lim in limits if lim["interaction"] != "full"]
        errors.append(f"Interaction: pages for {', '.join(capped)} have light interaction at most, so use 'Detail table: no'")
    if plan["reconcile"] and plan["review_depth"] != "deep":
        errors.append("review_depth: reconcile is on, so use 'review_depth: deep'")
    if "spec" in goals and len(goals) > 1:
        warnings.append("goals: spec builds exactly what was asked; a second goal usually adds blocks nobody asked for")
    if "monitor" in goals:
        if not any("target" in k for k in plan["kpis"]):
            warnings.append("Story: monitor goal without any KPI target, so the page can't show on/off track (add 'target>=N')")
        if not plan["last_updated"]:
            warnings.append("Interaction: monitor goal without '- Last updated: <date column>'")
    undrawn = [c["title"] for c in plan["charts"] if not c.get("draw")]
    if "impact" in goals and undrawn:
        errors.append(f'Story: the impact goal draws every chart in an unconventional form; add a "~ draw:" line under "{undrawn[0]}" (references/visual-language.md)')
    elif "spec" not in goals and undrawn:
        warnings.append(f'Story: no "~ draw:" line under {len(undrawn)} chart(s), e.g. "{undrawn[0]}"; pick each visual with references/visual-language.md')
    if "present" in goals and not any(c["note"] or c["annotations"] for c in plan["charts"]):
        warnings.append("Story: present goal without any narrative (> ...) or annotation (@ ...) under a chart")
    if cadence in ("daily", "weekly", "monthly") and not plan["comparison"]:
        warnings.append(f"comparison_period: {cadence} pages usually compare with the previous period, e.g. comparison_period: <date column>:{ {'daily': 'day', 'weekly': 'week', 'monthly': 'month'}[cadence]}")
    if cadence == "daily" and len(plan["charts"]) > MAX_DAILY_CHARTS:
        warnings.append(f"Story: daily pages are glanceable; {len(plan['charts'])} charts is more than {MAX_DAILY_CHARTS}")


def style_rules(plan, errors, warnings):
    """Check the Style Profile against the audience limits and the plan's own content."""
    if not plan.get("has_profile"):
        warnings.append("Style: no Style Profile; derive one with references/style-system.md and add it to ## Style")
        return
    style, audience = {k: v.lower() for k, v in plan["style"].items()}, plan["audience"]
    for a in audience:
        lim = AUDIENCE_LIMITS.get(a)
        if not lim:
            continue
        for field in ("density", "interaction", "motion"):
            if style.get(field) in ORDER[field] and ORDER[field].index(style[field]) > ORDER[field].index(lim[field]):
                errors.append(f"Style: {field} '{style[field]}' is above what {a} allows ('{lim[field]}' at most)")
        for field in ("provenance", "type_scale"):
            if style.get(field) in ORDER[field] and ORDER[field].index(style[field]) < ORDER[field].index(lim[field]):
                errors.append(f"Style: {field} '{style[field]}' is below what {a} needs ('{lim[field]}' at least)")
        banned = AUDIENCE_BANNED_FORMS.get(a, set())
        used_banned = sorted({c["form"] for c in plan["charts"]} & banned)
        if used_banned:
            errors.append(f"Story: {a} pages don't use {', '.join(used_banned)} (style-system.md, Audience overrides)")
    if "regulators" in audience:
        if style.get("numbers") != "exact":
            errors.append("Style: regulators need 'numbers: exact'")
        if style.get("register") != "evidentiary":
            errors.append("Style: regulators need 'register: evidentiary'")
    allowed = set(as_list(style.get("chart_set", "")))
    used = {c["form"] for c in plan["charts"]} | ({"kpis"} if plan["kpis"] else set())
    outside = sorted(used - allowed)
    if allowed and outside:
        errors.append(f"Style: the plan uses {', '.join(outside)}, which isn't in chart_set ({style.get('chart_set')})")
    if style.get("color_mode") in ("status", "diverging") and style.get("direction") == "none":
        errors.append(f"Style: color_mode '{style['color_mode']}' needs a direction (up-good or down-good)")
    cap = DENSITY_CAPS.get(style.get("density"))
    if style.get("surface") == "stage":
        # A stage shows one scene at a time (references/stage.md), so the cap is on scenes, not charts per screen.
        if not MIN_SCENES <= len(plan["charts"]) <= MAX_SCENES:
            errors.append(f"Style: a stage has {MIN_SCENES}–{MAX_SCENES} scenes (references/stage.md); the plan has {len(plan['charts'])}")
        cap = cap and (cap[0], len(plan["charts"]))
    if cap and (len(plan["kpis"]) > cap[0] or len(plan["charts"]) > cap[1]):
        errors.append(f"Style: density '{style['density']}' allows {cap[0]} KPIs and {cap[1]} charts; the plan has "
                      f"{len(plan['kpis'])} and {len(plan['charts'])}")
    if style.get("interaction") == "none" and (plan["menus"] or any(c["interaction"] != "none" for c in plan["charts"])):
        errors.append("Style: interaction 'none' but the plan has menus or brush/click charts")


def annotation_checks(con, plan, default, errors, warnings):
    """Annotations must point at something the chart actually shows."""
    for c in plan["charts"]:
        if not c["annotations"] or c["keys"].get("from", default) != default:
            continue
        where = f'"{c["title"]}"'
        for a in c["annotations"]:
            at = a["at"]
            try:
                if c["form"] == "bar":
                    col = c["keys"]["category"]
                    hit = con.execute(f'SELECT count(*) FROM {sql_str(default)} WHERE CAST("{col}" AS VARCHAR) = ?', [at]).fetchone()[0]
                    if not hit:
                        errors.append(f"{where}: annotation '@ {at}' is not a value of {col}")
                elif c["form"] == "trend":
                    col = c["keys"]["x"].partition(":")[0]
                    # A numeric time index (e.g. a day number) is annotated with a number, a date column with a date.
                    kind = con.execute(f'SELECT typeof("{col}") FROM {sql_str(default)} LIMIT 1').fetchone()[0]
                    cast = "TIMESTAMP" if any(t in kind for t in ("DATE", "TIME")) else "DOUBLE"
                    lo, hi, inside = con.execute(
                        f'SELECT min("{col}"), max("{col}"), CAST(? AS {cast}) BETWEEN min("{col}") AND max("{col}") FROM {sql_str(default)}', [at]).fetchone()
                    if not inside:
                        warnings.append(f"{where}: annotation '@ {at}' is outside the data ({lo} to {hi})")
                elif c["form"] in ("histogram", "scatter", "map"):
                    float(at)
                else:
                    errors.append(f"{where}: {c['form']} charts don't take annotations")
            except (duckdb.Error, ValueError) as e:
                errors.append(f"{where}: annotation '@ {at}' doesn't fit a {c['form']} chart: {str(e).splitlines()[0]}")


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    plan_path = Path(sys.argv[1])
    if not plan_path.exists():
        sys.exit(f"Plan not found: {plan_path}")
    text = plan_path.read_text(encoding="utf-8")
    plan, errors = parse(text)
    warnings = []
    if not plan:
        print("\n".join(f"ERROR {e}" for e in errors))
        sys.exit(1)

    prose = re.sub(r"```.*?```", "", text, flags=re.DOTALL)
    for ph in sorted(set(re.findall(r"\{[^{}\n]+\}", prose))):
        errors.append(f"Unfilled placeholder {ph}")

    sections = plan["sections"]
    goal_rules(plan, errors, warnings)
    style_rules(plan, errors, warnings)

    assumptions = sections.get("Assumptions", "").strip()
    if plan["review_depth"] == "quick" and re.fullmatch(r"(-\s*)?(none)?\.?", assumptions, re.IGNORECASE):
        errors.append("Assumptions: quick review asks no questions, so list what was assumed")

    data = sections.get("Data", "")
    if not re.search(r"Excluded:", data):
        errors.append("Data: add '- Excluded: ...' (write 'none' if nothing was excluded)")
    if plan["reconcile"] and not re.search(r"Reconcile with:", data):
        errors.append("Data: reconcile is on, so add '- Reconcile with: <source> (matched | not yet checked)'")
    for line in data.splitlines():
        if re.search(r"\brate\b|%", line, re.IGNORECASE) and "=" in line and not re.search(r"/| of | per ", line):
            warnings.append(f"Data: rate without a visible denominator: {line.strip()}")

    base = plan_path.resolve().parent
    os.chdir(base)
    con = duckdb.connect()
    src = plan["header"].get("source")
    if src and not Path(str(src)).exists():
        warnings.append(f"source {src} not found relative to the plan (fine if it is a database table)")

    columns = {}
    for f in plan["files"]:
        name, stated = str(f["file"]), f.get("rows")
        if not Path(name).exists():
            errors.append(f"data: {name} not found in {base}")
            continue
        try:
            columns[name] = {r[0] for r in con.execute(f"DESCRIBE SELECT * FROM {sql_str(name)}").fetchall()}
            actual = con.execute(f"SELECT count(*) FROM {sql_str(name)}").fetchone()[0]
            if stated is not None and int(stated) != actual:
                errors.append(f"data: {name} has {actual:,} rows, header says {stated}")
        except duckdb.Error as e:
            errors.append(f"data: cannot read {name}: {str(e).splitlines()[0]}")

    default = str(plan["files"][0]["file"]) if plan["files"] else None
    for file, col, where in columns_used(plan):
        file = file or default
        if file in columns and col not in columns[file]:
            errors.append(f"{where}: column '{col}' is not in {file}. Available: {', '.join(sorted(columns[file]))}")
        elif file and file not in columns and file not in [str(f["file"]) for f in plan["files"]]:
            errors.append(f"{where}: from={file} is not listed under data in the header")

    if default in columns:
        annotation_checks(con, plan, default, errors, warnings)

    for i, sql in enumerate(plan["sql"], 1):
        sql = sql.rstrip().rstrip(";")
        copy = re.match(r"COPY\s*\((.*)\)\s*TO\s", sql, re.IGNORECASE | re.DOTALL)
        try:
            con.execute(f"SELECT count(*) FROM ({copy.group(1) if copy else sql})").fetchone()
        except duckdb.Error as e:
            errors.append(f"SQL block {i} does not run: {str(e).splitlines()[0]}")

    for w in warnings:
        print(f"WARN  {w}")
    for e in errors:
        print(f"ERROR {e}")
    if errors:
        print(f"\n{len(errors)} error(s). Fix them and re-run.")
        sys.exit(1)
    print(f"Plan OK: {len(plan['kpis'])} KPIs, {len(plan['charts'])} charts, {len(plan['files'])} data file(s), {len(plan['sql'])} SQL block(s)")


if __name__ == "__main__":
    main()
