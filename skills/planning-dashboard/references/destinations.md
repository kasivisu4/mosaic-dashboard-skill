# Destinations

The destination decides what data the plan must export. It doesn't decide the chart library; that's the executor's job.

| Destination | Can the page run DuckDB? | Export |
|---|---|---|
| `local` (a file opened from disk, e.g. from Claude Code) | yes | the cleaned row-level table (exclusions applied) as Parquet |
| `self-hosted` | yes | same as `local` |
| `file` (one self-contained `report.html` to share: email, chat, any static host; opens by double-click, no server) | yes: the data is embedded in the page | a table small enough to embed: pre-aggregated to the grain the plan needs, Parquet with zstd, at most ~7.5 MB of Parquet: the page embeds it as base64, which grows it by about 4/3, so `report.html` stays under 10 MB (`bundle_report.py` warns above that) |
| `artifact` (a claude.ai artifact) | no: the DuckDB-WASM engine is larger than artifact file limits | a pre-aggregated table (below) |
| `dashboard-type` (claude.ai Dashboard artifact type) | no: small data files only | a pre-aggregated table, kept small |

## Picking one
1. The person named a destination → use it.
1b. The page will be shared, or nobody said → `file`: the person gets one `report.html` from `scripts/bundle_report.py` (SKILL.md step 5).
2. Working with a local filesystem and the person will open the file → `local`.
3. In a claude.ai chat → `artifact`.

## Large sources
When the profile says it was sampled (its `sample:` line), the row-level table is too big for DuckDB-WASM in a browser, whatever the destination. Export a pre-aggregated table (below) instead, and run the `COPY` against the source with the desktop DuckDB, which streams through it. State the grain under Assumptions.

## Pre-aggregated exports
When the page can't run DuckDB, export the smallest table that still supports every chart, KPI, and menu in the plan: typically one row per time bucket × each filter dimension, with sums and counts (never averages or rates; recompute those from sums and counts with `ratio(sum,count)` in the plan, so they stay correct under filtering). If it's still too large, drop the least important filter dimension and record that under Assumptions.
