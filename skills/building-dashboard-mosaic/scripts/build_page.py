"""Build a Mosaic + DuckDB-WASM dashboard page from a plan (plan format v2).

Usage: python build_page.py <plan.md> [--out index.html]

Reads the plan, fills the CONFIG block of assets/mosaic-dashboard.html, and writes
the page next to the plan (default name index.html). The data files listed in the
plan's header must sit next to the plan; the page loads them at runtime.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from plan_format import parse, parse_value  # noqa: E402

TEMPLATE = HERE.parent / "assets" / "mosaic-dashboard.html"


def sql_value(expr):
    agg, col = parse_value(expr)
    if agg == "count":
        return f'count("{col}")' if col else "count(*)"
    if agg == "rate":
        return f'avg(CAST("{col}" AS DOUBLE))'
    return f'{agg}("{col}")'


def chart_sql(chart, file):
    k, src = chart["keys"], f"'{k_file(chart, file)}'"
    if chart["form"] == "trend":
        col, _, bucket = k["x"].partition(":")
        return f"SELECT date_trunc('{bucket}', \"{col}\") AS x, {sql_value(k['y'])} AS y\nFROM {src}\nGROUP BY 1 ORDER BY 1"
    if chart["form"] == "bar":
        return f"SELECT \"{k['category']}\", {sql_value(k['value'])} AS value\nFROM {src}\nGROUP BY 1 ORDER BY 2 DESC"
    if chart["form"] == "histogram":
        return f"SELECT \"{k['value']}\"  -- binned in the chart\nFROM {src}"
    if chart["form"] == "scatter":
        return f"SELECT \"{k['x']}\", \"{k['y']}\"\nFROM {src}"
    if chart["form"] == "exceptions":
        op, limit = (">", k["above"]) if "above" in k else ("<", k["below"])
        order = "DESC" if op == ">" else "ASC"
        return f"SELECT \"{k['category']}\", {sql_value(k['value'])} AS value\nFROM {src}\nGROUP BY 1 HAVING value {op} {limit}\nORDER BY 2 {order}"
    return ""


def k_file(chart, default):
    return chart["keys"].get("from") or default


def table_name(file, i):
    stem = re.sub(r"\W+", "_", Path(file).stem).strip("_").lower() or "data"
    return stem if not stem[0].isdigit() else f"t{i}_{stem}"


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    plan_path = Path(args[0])
    out_name = args[args.index("--out") + 1] if "--out" in args else "index.html"
    if not plan_path.exists():
        sys.exit(f"Plan not found: {plan_path}")
    if not TEMPLATE.exists():
        sys.exit(f"Template missing: {TEMPLATE}")

    text = plan_path.read_text(encoding="utf-8")
    plan, errors = parse(text)
    if errors:
        print("The plan doesn't follow plan format v2, so the page can't be built:")
        print("\n".join(f"  - {e}" for e in errors))
        sys.exit("Fix the plan (the planner's scripts/validate_plan.py gives full checks) and run again.")

    base = plan_path.resolve().parent
    missing = [str(f["file"]) for f in plan["files"] if not (base / str(f["file"])).exists()]
    if missing:
        sys.exit(f"Data files not found next to the plan: {', '.join(missing)}")

    files = [str(f["file"]) for f in plan["files"]]
    default = files[0]
    config = {
        "title": plan["title"],
        "takeaway": plan["takeaway"],
        "goals": plan["goals"],
        "cadence": plan["cadence"],
        "comparison": plan["comparison"],
        "lastUpdated": plan["last_updated"],
        "successCriteria": plan["success_criteria"],
        "data": [{"table": table_name(f, i), "url": f} for i, f in enumerate(files)],
        "kpis": plan["kpis"],
        "charts": [
            {k: c[k] for k in ("title", "form", "keys", "interaction", "note", "annotations")} for c in plan["charts"]
        ],
        "menus": plan["menus"],
        "detailTable": plan["detail_table"],
        "sql": {c["title"]: chart_sql(c, default) for c in plan["charts"]} if plan["sql_on_page"] else {},
        "style": plan["style"],
        "buildNote": f"{text.strip()}\n\nBuilt by building-dashboard-mosaic on {date.today().isoformat()}.",
    }
    # Charts reading a non-default file can't join the page filter; say so instead of failing silently.
    for c in plan["charts"]:
        if c["keys"].get("from") and c["keys"]["from"] != default:
            print(f'NOTE  "{c["title"]}" reads {c["keys"]["from"]}, so it is not cross-filtered with the rest of the page.')

    js = json.dumps(config, indent=2, ensure_ascii=False).replace("</", "<\\/")
    page = TEMPLATE.read_text(encoding="utf-8")
    page, n = re.subn(r"const CONFIG = \{.*?\n\};", lambda m: f"const CONFIG = {js};", page, count=1, flags=re.DOTALL)
    if n != 1:
        sys.exit("Could not find the CONFIG block in the template.")
    out = base / out_name
    out.write_text(page, encoding="utf-8")
    print(f"Wrote {out}")
    if plan["success_criteria"]:
        print(f"Success criteria to check in review: {plan['success_criteria']}")
    print(f"Serve it:  cd \"{base}\" && python -m http.server 8000   then open http://localhost:8000/{out_name}")


if __name__ == "__main__":
    main()
