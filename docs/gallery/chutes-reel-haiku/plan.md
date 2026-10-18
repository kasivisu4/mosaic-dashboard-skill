---
plan_version: 2
goals: impact, explore
audience: clients
cadence: one-time
review_depth: quick
success_criteria: "none stated"
reconcile: false
destination: local
source: ../../../../../../kasivisu4.github.io/public/data/chutes/chutes.parquet
data:
  - file: traffic.parquet
    rows: 1337094
---

# One year of LLM traffic: 6.12 billion requests, April 2025 to April 2026

The traffic changed hands: DeepSeek carried most requests in May 2025 and Qwen passed it in March 2026, while the monthly total barely moved.

## Assumptions
- Family: the trace's `g_family` grouping (Unnamed, Other families and Long tail are kept as the trace groups them; they may shift with naming)
- Trace day: day 0 is 11 April 2025 (source paper arXiv:2608.13573); the trace clock is used for hours with no time zone
- Comparisons: "from X to Y" claims use full months only (May 2025 to March 2026); April 2025 and April 2026 are partial and are not compared
- Averages: ratios of sums (input and output tokens per call use calls with a count; time to first token uses streaming calls only)
- Units: time to first token is read in seconds (the file gives no unit)
- Gaps: days with missing hours are shown as gaps, not interpolated (13 January 2026 has 3 of 24 hours)

## Data
- 1 row = one day, hour, family and function group · 1,337,094 rows · 11 April 2025 to 12 April 2026 (367 days)
- Excluded: none
- Requests = sum(reqs) (confirmed)
- Input tokens per call = ratio(sum_it,n_it) (confirmed)
- Output tokens per call = ratio(sum_ot,n_ot) (confirmed)
- Time to first token = ratio(sum_ttft,n_ttft), streaming calls only, seconds (assumed)
- Share of a family = its requests divided by all requests in the same month (confirmed)

## Story
1. KPIs: Requests = sum(reqs) [compact]; Input tokens per call = ratio(sum_it,n_it) [compact]; Output tokens per call = ratio(sum_ot,n_ot) [compact]; Time to first token = ratio(sum_ttft,n_ttft) [number]
2. "DeepSeek fell from 84.4% of requests in May 2025 to 24.8% in March 2026; Qwen rose from 5.3% to 47.0%" | trend | x=day:month y=sum(reqs) color=g_family | none
   > Each month's requests by family, as a share of that month. Full months only.
   ~ draw: 100% stacked columns per month instead of a stacked area, so every family has a flat baseline; Qwen passes DeepSeek in March 2026 and that crossing is the moment to stop on
   @ 2026-03-01: Qwen passes DeepSeek
3. "Qwen's monthly requests rose from 18.5M in May 2025 to 156.6M in March 2026; its largest step came in December 2025" | trend | x=day:month y=sum(reqs) color=g_family | none
   > Small multiples on one shared scale, so each family's size is comparable. The step: 45.8M requests in November 2025, 132.5M in December 2025.
   ~ draw: small-multiple lines per family, each with the total as a grey ghost, morphing from the stacked columns; a shared y-scale
   @ 2025-12-01: Qwen's largest step
4. "The monthly total barely moved: 346M requests in May 2025, 333M in March 2026" | trend | x=day:month y=sum(reqs) color=g_family | none
   > Totals from full months only. The September 2025 peak (822M) is in the data and not in this comparison.
   ~ draw: 3D columns, one per family per month, height = requests (three data axes), read from an orbit camera with exact values on hover; flat floor, zero baseline
5. "Busiest day: 29 October 2025, with 34.9M requests" | trend | x=day:day y=sum(reqs) color=g_family | brush
   > Daily requests by family, each family in its own horizon band on a shared scale, with the full period on show.
   ~ draw: horizon bands for each family, morphing into a timeline of daily totals; the bands are the same days in the same order
   @ 2025-10-29: Busiest day (34.9M)
6. "13 January 2026 has 3 of 24 hours in the trace, so its 1.6M requests are not a real low" | trend | x=day:day y=sum(reqs) | none
   > Missing hours are shown as gaps, not as zero or interpolated. The file gives no cause.
   ~ draw: daily timeline bars with the gap marked; the same days as the horizon, with each day's bar keeping its height
   @ 2026-01-13: 3 of 24 hours recorded
7. "Requests peak at 13:00 on the trace clock: 285.6M, 18% above the 05:00 low" | bar | category=hod value=sum(reqs) | click
   > Requests by hour of day on the trace clock. The time zone is not in the file.
   ~ draw: radial clock with 24 hour segments, instead of bars, because the cycle is the finding; morphs to straight bars on click
   @ 13: Peak hour
8. "Time to first token rises with the daytime load: 2.09 s at 00:00, 2.50 s at 11:00" | bar | category=hod value=ratio(sum_ttft,n_ttft) | none
   > Streaming calls only. Across 367 days, the day's time to first token and Qwen's share of requests correlate at only 0.19, so the mix does not explain the latency.
   ~ draw: dot plot per hour on a zero-based axis with the all-day average as a rule, instead of bars; the dots morph from the clock
   @ 11: Slowest hour (2.50 s)
9. "Across the whole year, 55 of every 100 requests went to DeepSeek and 15 to Qwen" | bar | category=g_family value=sum(reqs) | none
   > Full year, all families, one unit = 1% of requests. The grouped families (Unnamed, Other families, Long tail) are shown as the trace groups them.
   ~ draw: waffle of 100 squares, one per percent of requests, morphing into unit bars; each family keeps its colour through the morph

## Interaction
- Menus: g_family
- Detail table: no
- SQL on page: no
- Last updated: day

## Style
- register: formal
- density: balanced
- surface: stage
- focus: the family gaining share (Qwen) and the crossing moments
- color_mode: categorical
- direction: none
- type_scale: display
- interaction: light
- motion: reveal
- chart_set: KPIs, trend, bar
- anomalies: spotlight
- narrative: annotated
- provenance: footnote
- numbers: rounded
- data_character: time-heavy, categorical, anomaly-rich, sparse
- accent: #efb118
- alert: #ff725c

## Data for the executor
```sql
COPY (SELECT date '2025-04-11' + dnum AS day, hod, g_family, reqs, sum_it, n_it, sum_ot, n_ot, sum_ttft, n_ttft FROM read_parquet('C:/Users/kasiv/projects/kasivisu4.github.io/public/data/chutes/chutes.parquet')) TO 'traffic.parquet' (FORMAT PARQUET, COMPRESSION ZSTD)
```
