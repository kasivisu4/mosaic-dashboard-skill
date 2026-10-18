"""Run your own exploratory queries against the data and save the SQL with its results.

Usage: python scripts/explore.py out/<name> <data file> <queries.sql> [--rows 25]

The profile (profile.py) is a fixed summary. After reading it, write the questions you still have as SQL in a
.sql file, one query per block, each headed by a "-- question" comment line:

    -- Which days are far below the median day?
    SELECT ... FROM t ...;

The data is available as table `t` (CSV, TSV, Parquet, JSON or a DuckDB table path). Each query runs on its own;
a failing query is reported with its error and the rest still run. Results go to out/<name>/1-profile/explore.md
(appended, so you can run several rounds), the SQL to 1-profile/explore.sql.
"""
import re
import sys
from datetime import datetime
from pathlib import Path

try:
    import duckdb
except ImportError:
    sys.exit("explore: duckdb is not installed; run: pip install duckdb")

# Rows shown per result: enough to read a ranking or a monthly series, short enough to keep explore.md readable.
DEFAULT_ROWS = 25


def die(msg):
    print(f"explore: {msg}", file=sys.stderr)
    sys.exit(1)


def reader(path):
    s = str(path).replace("'", "''")
    ext = path.suffix.lower()
    if ext in (".csv", ".tsv", ".txt"):
        return f"read_csv_auto('{s}')"
    if ext in (".json", ".ndjson", ".jsonl"):
        return f"read_json_auto('{s}')"
    if ext == ".parquet":
        return f"read_parquet('{s}')"
    die(f"can't read {path.name}: use CSV, TSV, Parquet or JSON (for Excel, export a CSV first)")


def blocks(sql_text):
    """[(question, sql)]: consecutive '-- ' lines form a block's question; the SQL lines after them its query."""
    out, question, buf = [], [], []
    def close():
        if any(l.strip() for l in buf):
            out.append((" ".join(question) or "(no question)", "\n".join(buf).strip().rstrip(";")))
    for line in sql_text.splitlines():
        m = re.match(r"^\s*--\s*(.+)$", line)
        if m and any(l.strip() for l in buf):
            close(); question, buf = [], []
        if m:
            question.append(m.group(1).strip())
        else:
            buf.append(line)
    close()
    return out


def table_md(cols, rows, limit):
    shown = rows[:limit]
    fmt = lambda v: "" if v is None else (f"{v:,.4g}" if isinstance(v, float) else str(v)).replace("|", "\\|")
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(fmt(v) for v in r) + " |" for r in shown]
    if len(rows) > limit:
        lines.append(f"\n({len(rows) - limit} more rows not shown)")
    return "\n".join(lines)


def main(argv):
    if len(argv) < 4:
        die("usage: python scripts/explore.py out/<name> <data file> <queries.sql> [--rows 25]")
    run, data, sql_file = Path(argv[1]), Path(argv[2]), Path(argv[3])
    args = dict(zip(argv[4::2], argv[5::2]))
    try:
        limit = int(args.get("--rows", DEFAULT_ROWS))
    except ValueError:
        die(f"--rows must be a whole number, got {args['--rows']!r}")
    if not run.is_dir():
        die(f"{run} is not a run folder; create it with start_run.py first")
    if not data.exists():
        die(f"data file not found: {data}")
    if not sql_file.exists():
        die(f"queries file not found: {sql_file}")
    qs = blocks(sql_file.read_text(encoding="utf-8"))
    if not qs:
        die(f"no queries found in {sql_file}; head each one with a '-- question' line")
    con = duckdb.connect()
    con.execute(f"CREATE VIEW t AS SELECT * FROM {reader(data)}")
    prof = run / "1-profile"
    prof.mkdir(parents=True, exist_ok=True)
    md = [f"\n## Round at {datetime.now():%Y-%m-%d %H:%M} ({len(qs)} queries)\n"]
    ok = 0
    for q, s in qs:
        md.append(f"### {q}\n\n```sql\n{s}\n```\n")
        try:
            res = con.execute(s)
            cols = [d[0] for d in res.description]
            md.append(table_md(cols, res.fetchall(), limit) + "\n")
            ok += 1
        except duckdb.Error as e:
            md.append(f"**Error:** {str(e).splitlines()[0]}\n")
    with open(prof / "explore.md", "a", encoding="utf-8") as f:
        f.write("\n".join(md))
    with open(prof / "explore.sql", "a", encoding="utf-8") as f:
        f.write(f"\n-- round at {datetime.now():%Y-%m-%d %H:%M}\n" + sql_file.read_text(encoding="utf-8") + "\n")
    print(f"{ok}/{len(qs)} queries ran; results in {prof / 'explore.md'}")
    if ok < len(qs):
        print("explore: some queries failed; their errors are in explore.md", file=sys.stderr)


if __name__ == "__main__":
    main(sys.argv)
