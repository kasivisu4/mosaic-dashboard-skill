"""A fast first look at a data file (well under a second for millions of rows, ~2 s for billions), for the intake form.

Usage: python quick_look.py <file> [--sheet NAME]

Reads the column list and summarizes a sample of rows (SAMPLE_ROWS), then picks the columns
the form's example text can mention: a date, a measure, a yes/no flag, and the dimensions
worth slicing. The full profile (profile.py) still runs separately, for the card's data definitions.
"""
import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from profile import LARGE_ROWS, classify, parquet_stats, refine, sample_sql, source_sql, total_rows  # noqa: E402

import duckdb  # noqa: E402  (profile.py already exits with a clear message if it's missing)

# Enough rows to classify columns reliably; summarizing this many takes ~15-65 ms at 8K-5M rows.
SAMPLE_ROWS = 20_000
# A large file is looked at in this many places (SAMPLE_ROWS // QUICK_PLACES rows each); each costs ~0.4 s.
QUICK_PLACES = 4
# A dimension worth suggesting has a handful of values: too few is a flag, too many is unreadable.
DIM_MIN, DIM_MAX = 3, 30


def look(path, sheet=None):
    con = duckdb.connect()
    path = path.replace(chr(92), '/')
    src = source_sql(con, path, sheet)
    total = total_rows(con, path, src)
    if total is not None and total <= LARGE_ROWS:
        sample = f"SELECT * FROM {src} USING SAMPLE {SAMPLE_ROWS} ROWS"
    else:  # USING SAMPLE reads every row: minutes on a large file
        sample = sample_sql(path, src, total, QUICK_PLACES, SAMPLE_ROWS // QUICK_PLACES)
    con.execute(f"CREATE TABLE t AS {sample}")
    cols = con.execute("DESCRIBE t").fetchall()
    rel = con.execute("SUMMARIZE t")
    idx = {d[0]: i for i, d in enumerate(rel.description)}
    rows = rel.fetchall()
    n = con.execute("SELECT count(*) FROM t").fetchone()[0] or 1
    # A mostly-empty column can look yes/no in a sample of a large file; the file's own max says otherwise.
    exact = parquet_stats(con, path, [(c[0], c[1]) for c in cols]) if total and total > LARGE_ROWS else {}
    columns = []
    for r in rows:
        name, dtype = r[idx["column_name"]], r[idx["column_type"]]
        distinct = int(r[idx["approx_unique"]] or 0)
        cls = classify(name, dtype, distinct, n)
        if cls == "flag" and dtype != "BOOLEAN" and name in exact and (exact[name][2] or 0) > 1:
            cls = "measure"
        columns.append({"name": name, "type": dtype, "class": cls, "distinct": distinct, "lo": r[idx["min"]], "hi": r[idx["max"]]})
    refined = refine({c["name"]: (c["class"], c["lo"], c["hi"]) for c in columns})
    for c in columns:
        c["class"] = refined[c["name"]]
    by_class = lambda c: [x["name"] for x in columns if x["class"] == c]  # noqa: E731
    dims = sorted((x for x in columns if x["class"] == "dimension" and DIM_MIN <= x["distinct"] <= DIM_MAX),
                  key=lambda x: x["distinct"])
    return {
        "columns": [{k: c[k] for k in ("name", "type", "class")} for c in columns],
        "all_columns": [c[0] for c in cols],
        "date": (by_class("date") or [None])[0],
        "measure": (by_class("measure") or [None])[0],
        "flag": (by_class("flag") or [None])[0],
        "cycle": (by_class("cycle") or [None])[0],
        "dims": [d["name"] for d in dims][:3],
    }


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    if not Path(args[0]).exists():
        sys.exit(f"File not found: {args[0]}")
    sheet = args[args.index("--sheet") + 1] if "--sheet" in args else None
    try:
        print(json.dumps(look(args[0], sheet), indent=2))
    except duckdb.Error as e:
        sys.exit(f"Could not read {args[0]}: {str(e).splitlines()[0]}")


if __name__ == "__main__":
    main()
