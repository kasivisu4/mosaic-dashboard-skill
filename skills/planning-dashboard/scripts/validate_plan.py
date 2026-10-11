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
from plan_format import columns_used, parse  # noqa: E402

try:
    import duckdb
except ImportError:
    sys.exit("duckdb is not installed. Run: pip install duckdb")

# Leadership and client pages are read in under a minute; more tiles than this stops being a summary.
MAX_SUMMARY_KPIS = 4
# Daily pages are glanceable: past this many charts they stop being a quick check.
MAX_DAILY_CHARTS = 4


def sql_str(path):
    return "'" + str(path).replace("'", "''") + "'"


def goal_rules(plan, errors, warnings):
    """Rules that follow from the intake fields (see guidelines/goals.md)."""
    goals, audience, cadence = plan["goals"], plan["audience"], plan["cadence"]
    summary = [a for a in audience if a in ("leadership", "clients")]
    if summary and plan["sql_on_page"]:
        errors.append(f"Interaction: pages for {', '.join(summary)} use 'SQL on page: no'")
    if summary and len(plan["kpis"]) > MAX_SUMMARY_KPIS:
        errors.append(f"Story: pages for {', '.join(summary)} have at most {MAX_SUMMARY_KPIS} KPIs, found {len(plan['kpis'])}")
    if ("explore" in goals or plan["review_depth"] == "deep") and not plan["detail_table"]:
        errors.append("Interaction: explore goals and deep review use 'Detail table: yes'")
    if plan["reconcile"] and plan["review_depth"] != "deep":
        errors.append("review_depth: reconcile is on, so use 'review_depth: deep'")
    if "spec" in goals and len(goals) > 1:
        warnings.append("goals: spec builds exactly what was asked; a second goal usually adds blocks nobody asked for")
    if "monitor" in goals:
        if not any("target" in k for k in plan["kpis"]):
            warnings.append("Story: monitor goal without any KPI target, so the page can't show on/off track (add 'target>=N')")
        if not plan["last_updated"]:
            warnings.append("Interaction: monitor goal without '- Last updated: <date column>'")
    if "present" in goals and not any(c["note"] or c["annotations"] for c in plan["charts"]):
        warnings.append("Story: present goal without any narrative (> ...) or annotation (@ ...) under a chart")
    if cadence in ("daily", "weekly", "monthly") and not plan["comparison"]:
        warnings.append(f"comparison_period: {cadence} pages usually compare with the previous period, e.g. comparison_period: <date column>:{ {'daily': 'day', 'weekly': 'week', 'monthly': 'month'}[cadence]}")
    if cadence == "daily" and len(plan["charts"]) > MAX_DAILY_CHARTS:
        warnings.append(f"Story: daily pages are glanceable; {len(plan['charts'])} charts is more than {MAX_DAILY_CHARTS}")


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
                    lo, hi, inside = con.execute(
                        f'SELECT min("{col}"), max("{col}"), CAST(? AS TIMESTAMP) BETWEEN min("{col}") AND max("{col}") FROM {sql_str(default)}', [at]).fetchone()
                    if not inside:
                        warnings.append(f"{where}: annotation '@ {at}' is outside the data ({lo} to {hi})")
                elif c["form"] in ("histogram", "scatter"):
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
