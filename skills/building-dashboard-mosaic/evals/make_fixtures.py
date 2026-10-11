"""Create executor eval inputs: a valid plan with its data, and a broken plan.

Usage (from the skill folder): python evals/make_fixtures.py
Writes evals/files/tickets/{tickets.csv, tickets_clean.parquet, plan.md} and evals/files/broken/plan.md.
"""
from pathlib import Path

import duckdb

out = Path(__file__).parent / "files"
tickets, broken = out / "tickets", out / "broken"
tickets.mkdir(parents=True, exist_ok=True)
broken.mkdir(parents=True, exist_ok=True)

# random() is only reproducible single-threaded, so the same data comes out on every run.
con = duckdb.connect()
con.execute("SET threads = 1")
con.execute("SELECT setseed(0.2)")
con.execute(f"""COPY (
  SELECT 'T' || i AS ticket_id,
         TIMESTAMP '2025-06-01' + to_minutes(CAST(floor(random() * 130000) AS BIGINT)) AS opened_at,
         ['Billing','Tech','Accounts'][1 + i % 3] AS team,
         ['low','medium','high','urgent'][1 + CAST(floor(random() * 4) AS INTEGER)] AS priority,
         CASE WHEN random() < 0.05 THEN NULL ELSE round(random() * 72, 1) END AS hours_to_resolve,
         CAST(floor(1 + random() * 5) AS INTEGER) AS csat
  FROM range(3000) t(i)) TO '{(tickets / "tickets.csv").as_posix()}' (HEADER)""")
con.execute(f"""COPY (SELECT * FROM '{(tickets / "tickets.csv").as_posix()}' WHERE hours_to_resolve IS NOT NULL)
  TO '{(tickets / "tickets_clean.parquet").as_posix()}'""")
rows = con.execute(f"SELECT count(*) FROM '{(tickets / 'tickets_clean.parquet').as_posix()}'").fetchone()[0]

(tickets / "plan.md").write_text(f"""---
plan_version: 1
persona: analyst
mode: deep
destination: local
source: tickets.csv
data:
  - file: tickets_clean.parquet
    rows: {rows}
---

# Support tickets, summer 2025

## Assumptions
- none

## Data
- 1 row = one ticket · {rows:,} rows · Jun–Aug 2025
- Excluded: tickets without a resolution time (still open)
- Avg resolution = avg(hours_to_resolve) over resolved tickets (confirmed)
- CSAT = average rating 1–5 (confirmed)

## Story
1. KPIs: Tickets = count() [compact]; Avg resolution (h) = avg(hours_to_resolve) [number]; Avg CSAT = avg(csat) [number]
2. "Tickets arrive at a steady daily rate" | trend | x=opened_at:day y=count() | brush
3. "Volume is split evenly across teams" | bar | category=team value=count() | click
4. "Resolution times spread evenly up to 72 hours" | histogram | value=hours_to_resolve | brush
5. "Slower tickets don't get lower ratings" | scatter | x=hours_to_resolve y=csat | brush

## Interaction
- Menus: priority
- Detail table: yes
- SQL on page: yes

## Style
- accent: #0f766e
- currency: USD

## Data for the executor
```sql
COPY (SELECT * FROM 'tickets.csv' WHERE hours_to_resolve IS NOT NULL) TO 'tickets_clean.parquet'
```
""", encoding="utf-8")

(broken / "plan.md").write_text("""---
plan_version: 1
persona: executive
mode: quick
destination: local
data:
  - file: missing.parquet
---

# Broken plan

## Story
1. KPIs: Revenue = total(revenue)
2. Revenue over time | line | x=date | drag
""", encoding="utf-8")

print(f"wrote tickets/ ({rows} rows) and broken/ under {out.as_posix()}")
