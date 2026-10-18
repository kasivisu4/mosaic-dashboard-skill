# Understand the data

`scripts/profile.py` reads CSV, TSV, Parquet, JSON/NDJSON, and Excel (`--sheet NAME`). For a database table, run the same steps as SQL against it. Write raw DuckDB SQL only for follow-ups.

## Focus on what the person named
If the request or the intake names measures, dimensions, or dates ("revenue by store over time"), map those words to column names and profile only them, plus any date column a trend needs:

```bash
python scripts/profile.py <file> --columns <measure>,<dimension>,<date column>
```

The output still lists the other columns by name and type, so a glossary term can still be matched later. If a word matches no column, put it on the confirmation card as an open question rather than guessing. With no columns named, profile everything.

## Recipe
1. **Summarize.** `SUMMARIZE t;` gives types, min/max, null %, approximate distinct counts.
2. **Grain.** What is one row? Test candidate keys: `SELECT count(*), count(DISTINCT (k1, k2)) FROM t;`
3. **Column classes.** date, measure (numeric, summable), dimension (low-cardinality category), flag (0/1 or boolean), id (high cardinality), text.
4. **Time coverage** (only if a date column exists). Min/max and gaps at the bucket the profiler suggests.
5. **Oddities.** Negative or zero measures, extreme values (p99 vs max), unexpected nulls, duplicate rows, mixed units, near-duplicate category spellings.
6. **Explore.** The profile is a fixed summary; your questions about *this* data aren't. Write the questions it raises (what's odd, what's big, what changed, what would explain it, whether a pattern holds within groups) as SQL, one block per question headed by a `-- question` line, and run them: `python scripts/explore.py out/<name> <data file> <queries.sql>`. The SQL and results are saved to `1-profile/explore.sql` and `explore.md`. Run as many rounds as the answers raise new questions; stop when the brief's angles have the numbers they need. A typical first round: grain and keys, time coverage and gaps, the largest categories and their share over time, outliers (top and bottom periods), and each candidate metric within its main dimension.
7. **Observations.** Write 3–5 plain sentences: grain, size, time span, dimensions worth slicing, and anything that needs a decision on the card.

## Choosing metrics
- Measures → sum, average, or median; flags → a rate (`avg(flag)`); ids → distinct counts.
- Prefer metrics the person named. Otherwise pick the 2–4 the profile supports and mark them *assumed*.
- Every rate needs an explicit denominator in the plan.
- Small-integer measures (ratings 1–5, scores 1–10) are usually ordinal: show distributions or averages, not sums.

## Data questions become card assumptions
Each oddity or ambiguity that would change a number becomes an assumption row on the confirmation card: the recommended choice is its value, and its Change button offers the alternatives. Patterns:
- *{rate}*: share of rows (alternative: share of *{measure}*)
- Exclusions: *{n}* negative *{measure}* values dropped as *{likely reason}* (alternative: keep them)
- *{column}*: *{p}*% empty, shown as "Unknown" (alternative: drop those rows)
- Grain: one row = *{inferred grain}* (alternative: *{other grain}*)

## Exporting data for the executor
Export with `COPY (…) TO '<name>.parquet'` next to the plan, apply the exclusions confirmed on the card, and put that exact statement in the plan's `## Data for the executor` section. What to export depends on the destination; see [destinations.md](destinations.md).
