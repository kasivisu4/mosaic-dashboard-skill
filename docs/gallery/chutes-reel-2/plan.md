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
    rows: 101821
---

# A year of LLM traffic

Over one year of traffic, model choice flipped: DeepSeek fell from 84% of requests in May 2025 to 25% in March 2026 while Qwen rose from 5% to 47%.

## Assumptions
- Review: quick, so no confirmation card; everything below was assumed from the request and the profile.
- Calendar: trace day 0 = 11 April 2025 (source paper), so the trace runs 2025-04-11 to 2026-04-12; April 2025 (20 days) and April 2026 (12 days) are partial months.
- Grain of the export: the source rollup summed to day × trace hour × family (model, function, streaming and category are dropped; the page never slices by them).
- Families in color: the five largest named families by requests (computed in the export); every other family, including the catch-all labels "Unnamed", "Long tail" and "Other named", is drawn as "Other" in muted ink. The family menu lists all 14.
- Monthly volume: drawn as requests per day of the month, so partial months compare fairly with full ones.
- Hour: the trace clock's hour (timezone not stated in the data).
- Latency: time to first token exists only for requests counted in n_ttft (streamed requests).
- Time strip: a daily-requests strip under the stage carries the time brush and Play (a 28-day window); month-unit scenes keep the whole year and show the window as a band.
- Colors: dark2 hues for the five families, deep blue focus for controls and the brushed window, orange-red reserved for breaches (none on this page).

## Data
- 1 row = trace day × trace hour × model family · 101,821 rows · 2025-04-11 to 2026-04-12 (367 days)
- Excluded: none
- Requests = sum of requests (assumed)
- Tokens = input tokens + output tokens (assumed)
- Output tokens per request = output tokens / requests with an output count, ratio of sums (assumed)
- Time to first token = summed seconds to first token / requests with a measured first token, ratio of sums, in seconds (assumed)

## Story
1. KPIs: Requests = sum(reqs) [compact]; Tokens = sum(tok) [compact]; Output tokens per request = ratio(tok_out,n_out) [number]; Time to first token = ratio(ttft_s,n_ttft) [number]
2. "DeepSeek served 55% of the trace's 6.12 billion requests" | bar | category=family value=sum(reqs) | click
   > One bar is the whole year; each family's length is its share of requests.
   ~ draw: single 100% bar with direct labels instead of a pie, one length to read; opens the show reel
   @ DeepSeek: 54.9% of requests
3. "Fourteen model families shared the year; DeepSeek and Qwen served 70%" | bar | category=family value=sum(reqs) | click
   > The same shares as areas, so the small families stay visible.
   ~ draw: the bar's segments split into a treemap of all 14 families (area = requests) instead of a ranked bar
   @ Qwen: 15.0% of requests
4. "Qwen grew from 0.6M to 5.1M requests a day while DeepSeek fell from 9.4M to 2.7M" | trend | x=day:month y=sum(reqs) color=fam6 | none
   > Each cell is one family in one month; darker means more requests a day.
   ~ draw: heat cells of requests per day (family × month) instead of a multi-line chart, the rows' fade and darkening is the story
   @ 2026-03-01: Last full month
5. "Traffic peaked in September 2025 at 27.4M requests a day" | trend | x=day:month y=sum(reqs) color=fam6 | none
   > The same cells rise into boxes: height is requests a day, from zero.
   ~ draw: heat cells rise into 3D bars (month × family × requests a day; three data axes, orbit by drag, exact values on hover) instead of a heatmap; morphs from the heat cells
   @ 2025-09-01: Peak month, 27.4M a day
6. "By March 2026 daily requests were back near May 2025's level: 10.7M against 11.2M" | trend | x=day:month y=sum(reqs) color=fam6 | none
   > The boxes settle into one stacked column per month.
   ~ draw: stacked bars of requests per day by family instead of a line, built from the same marks; partial months labelled
   @ 2025-04-11: Partial month (20 days)
   @ 2026-04-01: Partial month (12 days)
7. "Qwen overtook DeepSeek: 5% of requests in May 2025, 47% in March 2026" | trend | x=day:month y=sum(reqs) color=fam6 | none
   > Every column stretched to 100%: the mix, not the volume.
   ~ draw: stacked bars normalised to 100% instead of a stacked area; morphs from the stacked bars
   @ 2026-03-01: Qwen 47%, DeepSeek 25%
8. "By tokens, DeepSeek's share fell from 92% in May 2025 to 22% in March 2026" | trend | x=day:month y=sum(tok) color=fam6 | none
   > The measure changes to tokens (input + output); the columns join into a 100% area.
   ~ draw: 100% stacked area of token share instead of a multi-line chart; morphs from the 100% bars, title and axis name the new measure
   @ 2025-05-01: DeepSeek 92% of tokens
9. "13:00 on the trace clock carries 18.5% more requests than 22:00" | bar | category=hod value=sum(reqs) | none
   > All requests of the year, by hour of the trace clock.
   ~ draw: 24 hour bars in clock order instead of a ranked bar, the daily wave is the story
   @ 13: Busiest hour
10. "First tokens arrive slowest at 11:00 (2.50 s) and fastest at 23:00 (2.08 s)" | bar | category=hod value=ratio(ttft_s,n_ttft) format=number | none
   > The measure changes to time to first token, streamed requests only; the axis does not start at zero and says so.
   ~ draw: hour bars collapse into a dot plot of time to first token instead of a dual-axis line, one measure per axis
   @ 11: Slowest hour, 2.50 s
11. "The daily cycle deepened: the busiest hour was 1.14× the quietest in May 2025, 1.33× in March 2026" | trend | x=day:month y=sum(reqs) color=hod | none
   > One day-curve per month: requests per hour as a share of the month, on one shared scale.
   ~ draw: small-multiple day curves (one panel per month, shared y) instead of 13 overlaid lines
   @ 2025-05-01: 1.14× peak to trough
12. "Afternoons grew: 12:00–17:00 carried 26.1% of May's requests and 28.7% of March's" | trend | x=day:month y=sum(reqs) color=hod | none
   > The panels slide into overlapping rows, earliest month at the top.
   ~ draw: ridgeline of the monthly day curves instead of a stacked area; morphs from the small multiples
   @ 2026-03-01: 28.7% in 12:00–17:00
13. "In 10 of 11 full months the busiest hour fell between 12:00 and 15:00" | trend | x=day:month y=sum(reqs) color=hod | none
   > The rows square up into cells: month × hour, darker means a larger share of the month.
   ~ draw: heatmap of month × hour with a legend instead of a line chart; morphs from the ridgeline
   @ 2025-09-01: September peaked at 02:00

## Interaction
- Menus: family
- Detail table: no
- SQL on page: no
- Last updated: day

## Style
- register: editorial
- density: balanced
- surface: stage
- focus: the family that is rising or falling in the current scene
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
- accent: #2b5c8a
- alert: #c2410c

## Data for the executor
```sql
COPY (
  WITH src AS (SELECT * FROM '../../../../../../kasivisu4.github.io/public/data/chutes/chutes.parquet'),
  top5 AS (
    SELECT family FROM src
    WHERE family NOT IN ('Unnamed', 'Long tail', 'Other named')
    GROUP BY family ORDER BY sum(reqs) DESC LIMIT 5
  )
  SELECT DATE '2025-04-11' + dnum::INT AS day, dnum::INT AS dnum, hod::INT AS hod, s.family,
         CASE WHEN s.family IN (SELECT family FROM top5) THEN s.family ELSE 'Other' END AS fam6,
         sum(reqs)::DOUBLE AS reqs,
         sum(coalesce(sum_it, 0))::DOUBLE AS tok_in, sum(n_it)::DOUBLE AS n_in,
         sum(coalesce(sum_ot, 0))::DOUBLE AS tok_out, sum(n_ot)::DOUBLE AS n_out,
         sum(coalesce(sum_it, 0) + coalesce(sum_ot, 0))::DOUBLE AS tok,
         sum(coalesce(sum_ttft, 0))::DOUBLE AS ttft_s, sum(n_ttft)::DOUBLE AS n_ttft
  FROM src s
  GROUP BY ALL
  ORDER BY day, hod, s.family
) TO 'traffic.parquet' (FORMAT parquet, COMPRESSION zstd)
```
