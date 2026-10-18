---
plan_version: 2
goals: impact, explore
audience: clients
cadence: one-time
review_depth: quick
success_criteria: "none stated; assumed: the year's shape of LLM traffic and its biggest shift (the DeepSeek-to-Qwen handover) are obvious in five seconds, and volume, tokens, latency and model mix can be explored by time and category"
reconcile: false
destination: file
source: ../../../../../../kasivisu4.github.io/public/data/chutes/chutes.parquet
data:
  - file: chutes_daily_hourly.parquet
    rows: 247258
---

# A year of LLM traffic on Chutes

Over 6.12 billion requests between April 2025 and April 2026, the platform's traffic changed hands: DeepSeek served 84.4% of requests in May 2025 and 24.8% in March 2026, while Qwen rose from 5.3% to 47.0%.

## Assumptions
- Success criteria: none were stated; assumed the handover and the year's volume curve must be readable in five seconds
- Grain: exported at day × trace hour × model family × category (sums and counts), small enough to embed; model-level and streaming-level detail are dropped
- Families: the five largest named families keep their own colour (DeepSeek, Qwen, Gemma, Mistral, GLM); the other nine (including "Unnamed" UUID models and the "Long tail" outside the top 200) are grouped as "Other families"
- Requests a day: monthly figures are divided by the days present in that month, so the partial first and last months (20 and 12 days) compare fairly
- From-to claims: first and last full months (May 2025 and March 2026)
- Trace clock: hour of day is the trace's own clock (hod), not a stated time zone
- Bead unit: one bead = 10 million requests, rounded per month with largest remainders so each month's beads add up to its rounded total
- Incomplete days: 13 Jan 2026 (3 of 24 hours) and 14 Jan 2026 (15 hours) are kept and marked as incomplete, not dropped
- Colors: Okabe–Ito categorical hues per family on the seed's midnight theme; yellow marks incomplete data
- Angles: the bead abacus of volume and mix; the DeepSeek-to-Qwen handover in requests a day and in share; latency by family and month; the busiest and emptiest days; weekly and hourly rhythm

## Data
- 1 row = one trace day × trace hour × model family × request category, with sums and counts · 247,258 rows · 11 Apr 2025 – 12 Apr 2026 (day 0 = 11 Apr 2025, per arXiv:2608.13573)
- Excluded: none (rows without token or latency values count toward requests only)
- Requests = sum of reqs (assumed)
- Avg input tokens = sum_it / n_it, requests with an input-token count (assumed)
- Avg output tokens = sum_ot / n_ot, requests with an output-token count (assumed)
- Avg time to first token = sum_ttft / n_ttft in seconds, streaming calls only (assumed)
- Family share = a family's requests / all requests in the same month (assumed)

## Story
1. KPIs: Requests = sum(reqs) [compact]; Avg input tokens = ratio(sum_it,n_it) [number]; Avg output tokens = ratio(sum_ot,n_ot) [number]; Avg time to first token = ratio(sum_ttft,n_ttft) [number]
2. "One bead per 10 million requests: DeepSeek served 84.4% of May 2025, Qwen 47.0% of March 2026" | trend | x=d:month y=sum(reqs) color=fam | none
   > Each month is a rod; its beads stack from the floor in family order, so height is volume and colour is the mix. Volume peaked in September 2025 at 27.4M requests a day, 2.45× May.
   ~ draw: invented bead abacus (one bead = 10M requests, a rod per month, beads stacked by family) instead of monthly stacked columns, so totals are countable units and the mix is visible at once
   @ 2025-09-01: Peak month, 27.4M requests a day
3. "DeepSeek carried 54.9% of the year's requests, more than the other 13 families combined" | bar | category=fam value=sum(reqs) | click
   > The same beads roll off their rods into one heap per family.
   ~ draw: unit bars (the beads regrouped into one heap per family, ranked) instead of a sorted bar chart, so the year's totals are bead counts
4. "DeepSeek fell from 9.4M to 2.7M requests a day while Qwen rose from 0.6M to 5.1M (May 2025 → Mar 2026)" | trend | x=d:month y=sum(reqs) color=fam | none
   > Requests a day per family and month, one panel per family on a shared scale.
   ~ draw: small-multiple bars on a shared y (requests a day) instead of a multi-line chart; the beads shrink into these cells
5. "Qwen passed DeepSeek in March 2026: 47.0% of requests against 24.8%, after 5.3% against 84.4% in May 2025" | trend | x=d:month y=sum(reqs) color=fam | none
   > The same cells slide out of their panels and stack into each month's 100%.
   ~ draw: morphs from the small multiples into 100% stacked columns with direct labels, instead of a stacked area, so each month's share is one length to read
   @ 2026-03-01: Qwen passes DeepSeek
6. "First tokens got faster, then slower: DeepSeek took 3.02 s in May 2025, 1.56 s in Sep, 3.34 s in Mar 2026" | trend | x=d:month y=ratio(sum_ttft,n_ttft) color=fam | none
   > Same family × month cells, re-coloured by a new measure: average time to first token (streaming calls only).
   ~ draw: heat cells (family × month, sequential colour with legend) instead of one latency line per family
7. "Seen as a skyline: DeepSeek's tallest month was Jun 2025 at 15.2M requests a day; Qwen's was Jan 2026 at 5.6M" | trend | x=d:month y=sum(reqs) color=fam | none
   > The heat cells rise into boxes: month × family × requests a day, three data axes; drag to turn it.
   ~ draw: 3D bars (d3-3d) rising out of the heat cells instead of grouped bars, so the shift of the tall ridge from DeepSeek to Qwen reads as a landscape
8. "The busiest day, 29 Oct 2025, had 34.9M requests; 13 Jan 2026 logged only 1.6M (3 of 24 hours recorded)" | trend | x=d:day y=sum(reqs) | brush
   > One dot per day. The time strip in the rail is this chart's brush: drag it, or press Play.
   ~ draw: day strip (a dot per day on the time axis, y = requests that day) instead of a daily line, so the outage is a missing day, not a dip in a curve
   @ 2026-01-13: Only 3 of 24 hours recorded
9. "No weekly rhythm to speak of: Wednesdays average only 7.2% more requests than Saturdays" | trend | x=d:day y=sum(reqs) | none
   > The same days wind into a spiral, one turn per week; dot area = requests that day.
   ~ draw: weekly spiral (angle = weekday, radius = week, area = requests) instead of a weekday bar chart, so every week's rhythm is visible, not only the average
10. "Traffic barely sleeps: the busiest trace hour (13) has only 1.19× the requests of the quietest (22)" | bar | category=hod value=sum(reqs) | none
   > Requests by hour of the trace clock, summed over the selection.
   ~ draw: hour bars on a zero baseline, kept conventional for one scene because the next scene bends them into a clock
11. "Latency follows the clock: first tokens take 2.50 s at hour 11 and 2.08 s at hour 23" | bar | category=hod value=ratio(sum_ttft,n_ttft) | none
   > The hour bars bend into a 24-hour ring and switch measure to average time to first token.
   ~ draw: morphs to radial bars (24-hour clock, bar length linear from an inner ring) instead of a line by hour, since the trace clock is a cycle

## Interaction
- Menus: category
- Detail table: no
- SQL on page: no
- Last updated: d

## Style
- register: formal
- density: balanced
- surface: stage
- focus: the DeepSeek-to-Qwen handover
- color_mode: categorical
- direction: none
- type_scale: display
- interaction: light
- motion: reveal
- chart_set: KPIs, bar, trend
- anomalies: explain
- narrative: annotated
- provenance: footnote
- numbers: rounded
- data_character: time-heavy, categorical, high-cardinality, anomaly-rich, sparse
- accent: #e69f00
- alert: #f0e442

## Data for the executor
```sql
COPY (
  SELECT (DATE '2025-04-11' + dnum::INT) AS d, dnum, hod, family,
         CASE WHEN family IN ('DeepSeek','Qwen','Gemma','Mistral','GLM') THEN family ELSE 'Other families' END AS fam,
         category,
         sum(reqs)::BIGINT AS reqs, sum(sum_it)::BIGINT AS sum_it, sum(n_it)::BIGINT AS n_it,
         sum(sum_ot)::BIGINT AS sum_ot, sum(n_ot)::BIGINT AS n_ot,
         sum(sum_ttft)::DOUBLE AS sum_ttft, sum(n_ttft)::BIGINT AS n_ttft
  FROM '../../../../../../kasivisu4.github.io/public/data/chutes/chutes.parquet'
  GROUP BY ALL ORDER BY d, hod, family, category
) TO 'chutes_daily_hourly.parquet' (FORMAT parquet, COMPRESSION zstd)
```
