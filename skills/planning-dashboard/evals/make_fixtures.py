"""Generate eval input files from unrelated domains into evals/files/.

Usage (from the skill folder): python evals/make_fixtures.py
"""
from pathlib import Path

import duckdb

out = Path(__file__).parent / "files"
out.mkdir(exist_ok=True)
o = out.as_posix()
# random() is only reproducible single-threaded, so the same data comes out on every run.
con = duckdb.connect()
con.execute("SET threads = 1")
con.execute("SELECT setseed(0.1)")

# Retail orders: a year of dates, a measure, a flag, two dimensions.
con.execute(f"""COPY (
  SELECT i AS order_id,
         DATE '2025-01-01' + CAST(floor(random() * 365) AS INTEGER) AS order_date,
         ['North','South','East','West'][1 + i % 4] AS store,
         ['Shoes','Bags','Hats','Coats','Socks'][1 + CAST(floor(random() * 5) AS INTEGER)] AS category,
         round(10 + random() * 190, 2) AS revenue,
         (random() < 0.08) AS returned
  FROM range(8000) t(i)) TO '{o}/orders.parquet'""")

# Support tickets: timestamps, a duration with nulls, an ordinal rating.
con.execute(f"""COPY (
  SELECT 'T' || i AS ticket_id,
         TIMESTAMP '2025-06-01' + to_minutes(CAST(floor(random() * 130000) AS BIGINT)) AS opened_at,
         ['Billing','Tech','Accounts'][1 + i % 3] AS team,
         ['low','medium','high','urgent'][1 + CAST(floor(random() * 4) AS INTEGER)] AS priority,
         CASE WHEN random() < 0.05 THEN NULL ELSE round(random() * 72, 1) END AS hours_to_resolve,
         CAST(floor(1 + random() * 5) AS INTEGER) AS csat
  FROM range(3000) t(i)) TO '{o}/tickets.csv' (HEADER)""")

# Employee survey: no date column at all.
con.execute(f"""COPY (
  SELECT ['Engineering','Sales','Support','Ops'][1 + i % 4] AS department,
         ['<1y','1-3y','3-5y','5y+'][1 + CAST(floor(random() * 4) AS INTEGER)] AS tenure,
         CAST(floor(1 + random() * 10) AS INTEGER) AS satisfaction,
         (random() < 0.3) AS considering_leaving
  FROM range(600) t(i)) TO '{o}/survey.json'""")

print(f"wrote orders.parquet, tickets.csv, survey.json to {o}")
