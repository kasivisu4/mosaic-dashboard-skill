# Destinations

The destination decides what data the plan must export. It doesn't decide the chart library; that's the executor's job.

| Destination | Can the page run DuckDB? | Export |
|---|---|---|
| `local` (a file opened from disk, e.g. from Claude Code) | yes | the cleaned row-level table (exclusions applied) as Parquet |
| `self-hosted` | yes | same as `local` |
| `artifact` (a claude.ai artifact) | no: the DuckDB-WASM engine is larger than artifact file limits | a pre-aggregated table (below) |
| `dashboard-type` (claude.ai Dashboard artifact type) | no: small data files only | a pre-aggregated table, kept small |

## Picking one
1. The person named a destination → use it.
2. Working with a local filesystem and the person will open the file → `local`.
3. In a claude.ai chat → `artifact`.

## Pre-aggregated exports
When the page can't run DuckDB, export the smallest table that still supports every chart, KPI, and menu in the plan: typically one row per time bucket × each filter dimension, with sums and counts (never averages or rates; recompute those from sums and counts so they stay correct under filtering). If it's still too large, drop the least important filter dimension and record that under Assumptions.
