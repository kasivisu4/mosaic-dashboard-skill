"""Compact DuckDB profile of any tabular file.

Usage: python profile.py <file> [--sheet NAME] [--columns col,col]

--columns  profile only these columns (the ones the person named); the rest are listed by name and type only

Large files (over LARGE_ROWS rows, or a non-Parquet file over LARGE_BYTES) are profiled on a sample
and the output says so. For Parquet the row count, null% and min/max stay exact (file metadata).
Formats: .csv .tsv .txt .parquet .json .ndjson .jsonl .xlsx (anything else is read as delimited text)
"""
import sys
from pathlib import Path

try:
    import duckdb
except ImportError:
    sys.exit("duckdb is not installed. Run: pip install duckdb")

NUMERIC = ("INT", "DECIMAL", "DOUBLE", "FLOAT", "REAL", "NUMERIC")
# A column whose distinct count is at least this share of rows behaves like an identifier.
ID_SHARE = 0.95
# SUMMARIZE's distinct counts are estimates (off by ~10%); below this many rows count exactly.
EXACT_DISTINCT_ROWS = 5_000_000
# Above this many distinct values a text column is free text, not a useful filter dimension.
MAX_DIMENSION = 200
# Past this many rows a full scan takes minutes (a 91 GB, 6.1B-row Parquet file: ~100 s per pass,
# and SELECT DISTINCT * runs out of memory), so large files are profiled on a sample instead.
LARGE_ROWS = 20_000_000
# Non-Parquet files can't be counted without reading them all; past this size, read only the start.
LARGE_BYTES = 2_000_000_000
# A large Parquet file is sampled at this many evenly spaced places, SAMPLE_RUN rows each.
# Each place costs ~0.4 s (DuckDB skips the row groups in between), so 24 places take ~10 s.
SAMPLE_PLACES = 24
SAMPLE_RUN = 4096


def source_sql(con, path, sheet=None):
    ext = Path(path).suffix.lower()
    p = path.replace("'", "''")
    if ext == ".parquet":
        return f"read_parquet('{p}')"
    if ext in (".json", ".ndjson", ".jsonl"):
        return f"read_json_auto('{p}')"
    if ext in (".xlsx", ".xls"):
        con.execute("INSTALL excel; LOAD excel;")
        return f"read_xlsx('{p}'" + (f", sheet='{sheet}')" if sheet else ")")
    return f"read_csv_auto('{p}', sample_size=-1)"


def total_rows(con, path, src):
    """Exact row count when it's cheap: Parquet metadata, or a count of a file under LARGE_BYTES. Else None."""
    if Path(path).suffix.lower() == ".parquet":
        p = path.replace("'", "''")
        return con.execute(f"SELECT num_rows FROM parquet_file_metadata('{p}')").fetchone()[0]
    if Path(path).stat().st_size > LARGE_BYTES:
        return None
    return con.execute(f"SELECT count(*) FROM {src}").fetchone()[0]


def sample_sql(path, src, rows, places=SAMPLE_PLACES, run=SAMPLE_RUN):
    """Rows from across a large file without reading all of it.

    Parquet: `places` runs of `run` rows at evenly spaced row numbers, one subquery each, so DuckDB
    reads only the row groups holding them. (USING SAMPLE, even SYSTEM, still reads every row group.)
    Other formats can't seek, so: the first places*run rows.
    """
    if Path(path).suffix.lower() == ".parquet" and rows:
        p = path.replace("'", "''")
        step = max(rows // places, run)
        parts = [f"(SELECT * EXCLUDE (file_row_number) FROM read_parquet('{p}', file_row_number=true)"
                 f" WHERE file_row_number BETWEEN {i * step} AND {i * step + run - 1})"
                 for i in range(places) if i * step < rows]
        return " UNION ALL ".join(parts)
    return f"SELECT * FROM {src} LIMIT {places * run}"


def parquet_stats(con, path, cols):
    """Exact null counts and min/max per column from Parquet row-group statistics (no data read)."""
    if Path(path).suffix.lower() != ".parquet":
        return {}
    p = path.replace("'", "''")
    # Read the footer once (~0.5 s for 6,000 row groups); the per-column queries below hit this small table.
    con.execute("CREATE TEMP TABLE IF NOT EXISTS pq_stats AS SELECT path_in_schema AS col, stats_null_count AS nulls,"
                f" stats_min AS lo, stats_max AS hi FROM parquet_metadata('{p}')")
    out = {}
    for name, dtype in cols:
        try:
            out[name] = con.execute(
                f"SELECT sum(nulls), min(TRY_CAST(lo AS {dtype})), max(TRY_CAST(hi AS {dtype}))"
                " FROM pq_stats WHERE col = ?", [name]).fetchone()
        except duckdb.Error:  # nested or unusual types have no usable statistics
            continue
    return out


def classify(name, dtype, distinct, rows):
    t, n = dtype.upper(), name.lower()
    if (n == "id" or n.endswith("id")) and distinct >= rows * 0.5:
        return "id"
    if "DATE" in t or "TIME" in t:
        return "date"
    if t == "BOOLEAN" or (distinct <= 2 and any(k in t for k in NUMERIC)):
        return "flag"
    if any(k in t for k in NUMERIC):
        return "id" if "INT" in t and distinct >= rows * ID_SHARE else "measure"
    if distinct >= rows * ID_SHARE:
        return "id"
    return "dimension" if distinct <= MAX_DIMENSION else "text"


def time_bucket(con, col):
    days = con.execute(f"SELECT date_diff('day', min({col}), max({col})) FROM t").fetchone()[0] or 0
    # ~90 points per chart keeps trends readable at any of these buckets.
    return "day" if days <= 90 else "week" if days <= 730 else "month"


def main():
    args = sys.argv[1:]
    if not args or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    path = args[0].replace("\\", "/")
    sheet = args[args.index("--sheet") + 1] if "--sheet" in args else None
    wanted = []
    if "--columns" in args:
        i = args.index("--columns")
        if i + 1 >= len(args):
            sys.exit("--columns needs a comma-separated list, e.g. --columns order_date,revenue")
        wanted = [c.strip() for c in args[i + 1].split(",") if c.strip()]
    if not Path(path).exists():
        sys.exit(f"File not found: {path}")

    con = duckdb.connect()
    try:
        src = source_sql(con, path, sheet)
        total = total_rows(con, path, src)
        sampled = total is None or total > LARGE_ROWS
        if sampled:  # everything below reads this sample; `total` stays the file's real size
            con.execute(f"CREATE TABLE t AS {sample_sql(path, src, total)}")
        else:
            con.execute(f"CREATE VIEW t AS SELECT * FROM {src}")
        rows = con.execute("SELECT count(*) FROM t").fetchone()[0] if sampled else total
    except duckdb.Error as e:
        sys.exit(f"Could not read {path}: {e}")
    if rows == 0:
        sys.exit(f"{path} has no rows")

    dupes = rows - con.execute("SELECT count(*) FROM (SELECT DISTINCT * FROM t)").fetchone()[0]
    all_cols = con.execute("DESCRIBE t").fetchall()  # rows of (name, type, ...)
    exact = parquet_stats(con, path, [(c[0], c[1]) for c in all_cols]) if sampled else {}
    others = []
    if wanted:
        by_lower = {c[0].lower(): c[0] for c in all_cols}
        missing = [w for w in wanted if w.lower() not in by_lower]
        if missing:
            sys.exit(f"Not in {path}: {', '.join(missing)}. Columns: {', '.join(c[0] for c in all_cols)}")
        keep = [by_lower[w.lower()] for w in wanted]
        others = [f"{c[0]} ({c[1]})" for c in all_cols if c[0] not in keep]
        cols = ", ".join('"' + k.replace('"', '""') + '"' for k in keep)
        con.execute(f"CREATE VIEW focus AS SELECT {cols} FROM t")
        summary = con.execute("SUMMARIZE focus").fetchall()
    else:
        summary = con.execute("SUMMARIZE t").fetchall()
    idx = {d[0]: i for i, d in enumerate(con.description)}

    print(f"# Profile: {path}")
    if sampled:
        size = f"{total:,}" if total else f"not counted ({Path(path).stat().st_size / 1e9:.0f} GB file)"
        where = f"{SAMPLE_PLACES} places spread across the file" if total else "the start of the file"
        print(f"rows: {size}   columns: {len(all_cols)}   duplicate rows in the sample: {dupes:,}")
        print(f"sample: profiled {rows:,} rows from {where}; distinct counts, shares and percentiles are from the"
              f" sample{', null% and range are exact (file metadata)' if exact else ''}")
    else:
        print(f"rows: {rows:,}   columns: {len(all_cols)}   duplicate rows: {dupes:,}")
    if others:
        print(f"profiled: {len(summary)} requested column(s); not profiled: {', '.join(others)}")
    print()
    print(f"{'column':<22}{'type':<12}{'class':<11}{'distinct':>9}{'null%':>7}  range")
    classes = {}
    for r in summary:
        name, dtype = r[idx["column_name"]], r[idx["column_type"]]
        distinct = int(r[idx["approx_unique"]] or 0)
        if rows <= EXACT_DISTINCT_ROWS:
            q = '"' + name.replace('"', '""') + '"'
            distinct = con.execute(f"SELECT count(DISTINCT {q}) FROM t").fetchone()[0]
        null_pct = float(r[idx["null_percentage"]] or 0)
        lo, hi = r[idx["min"]], r[idx["max"]]
        if name in exact:
            nulls, lo_x, hi_x = exact[name]
            null_pct = 100 * (nulls or 0) / total
            lo, hi = (lo_x, hi_x) if lo_x is not None else (lo, hi)
        cls = classes[name] = classify(name, dtype, distinct, rows)
        rng = f"{lo} .. {hi}"
        print(f"{name[:21]:<22}{dtype[:11]:<12}{cls:<11}{distinct:>9,}{null_pct:>6.1f}%  {rng[:48]}")

    notes = []
    for name, cls in classes.items():
        q = '"' + name.replace('"', '""') + '"'
        if name in exact:
            nulls, of = exact[name][0] or 0, total
        else:
            nulls, of = con.execute(f"SELECT count(*) FILTER ({q} IS NULL) FROM t").fetchone()[0], rows
        if nulls:
            notes.append(f"{name}: {nulls:,} nulls ({nulls / of:.1%}){' in the sample' if sampled and of == rows else ''}")
        if cls == "measure":
            neg, zero, p99, mx, distinct = con.execute(
                f"SELECT count(*) FILTER ({q} < 0), count(*) FILTER ({q} = 0),"
                f" quantile_cont({q}, 0.99), max({q}), count(DISTINCT {q}) FROM t"
            ).fetchone()
            if name in exact and exact[name][2] is not None:
                mx = exact[name][2]  # the file's true max, not the sample's
            if neg:
                notes.append(f"{name}: {neg:,} negative values")
            if zero > rows * 0.2:
                notes.append(f"{name}: {zero / rows:.0%} zeros")
            if p99 and mx and p99 > 0 and mx > 10 * p99:
                notes.append(f"{name}: max {mx:,.2f} is more than 10x p99 {p99:,.2f}")
            if distinct <= 11:
                notes.append(f"{name}: only {distinct} distinct values, likely ordinal (rating/score)")
        elif cls == "flag":
            rate = con.execute(f"SELECT avg({q}::DOUBLE) FROM t").fetchone()[0]
            notes.append(f"{name}: rate {rate:.2%}")
        elif cls == "date" and sampled:  # short runs of rows can't show gaps; report the span only
            lo, hi = exact[name][1:] if name in exact else (None, None)
            if lo is None:
                lo, hi = con.execute(f"SELECT min({q}), max({q}) FROM t").fetchone()
            notes.append(f"{name}: {lo} to {hi}; gaps not checked (sampled)")
        elif cls == "date":
            b = time_bucket(con, q)
            n, gaps = con.execute(
                f"""WITH w AS (SELECT DISTINCT date_trunc('{b}', {q}) x FROM t WHERE {q} IS NOT NULL)
                    SELECT count(*), date_diff('{b}', min(x), max(x)) + 1 - count(*) FROM w"""
            ).fetchone()
            notes.append(f"{name}: {n} {b}s covered, {gaps} missing (suggested bucket: {b})")
        elif cls == "dimension":
            top = con.execute(f"SELECT {q}, count(*) c FROM t GROUP BY 1 ORDER BY c DESC LIMIT 3").fetchall()
            notes.append(f"{name}: top " + ", ".join(f"{v} ({c / rows:.0%})" for v, c in top))

    print("\n## Observations")
    for n in notes or ["nothing notable"]:
        print(f"- {n}")
    print("\n## Column classes")
    for cls in ("date", "measure", "flag", "dimension", "id", "text"):
        cols = [c for c, k in classes.items() if k == cls]
        if cols:
            print(f"- {cls}: {', '.join(cols)}")


if __name__ == "__main__":
    main()
