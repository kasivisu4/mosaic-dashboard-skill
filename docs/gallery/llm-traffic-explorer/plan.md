---
plan_version: 2
goals: impact, explore
audience: clients
cadence: one-time
review_depth: quick
success_criteria: "how request volume, token usage, latency and model mix changed over the year is visible and explorable; a technical section explains source, aggregation and limits"
reconcile: false
destination: local
source: ../../../../../../kasivisu4.github.io/public/data/chutes/chutes.parquet
data:
  - file: traffic.parquet
    rows: 396205
---

# A year of LLM traffic on Chutes

6.12 billion requests from 11 April 2025 to 12 April 2026: Qwen overtook DeepSeek in March 2026. September 2025 was the odd month (peak volume, fastest first token, shortest prompts, with a Gemma surge); by March speed and prompt size were back to spring levels, and only GLM kept slowing.

## Assumptions
- Calendar: trace day 0 = 11 April 2025, from the source paper's stated span (2025-04-11 to 2026-04-12); the file itself has no dates
- Hour of day: the trace's own clock, not a known timezone; shown as "trace hour"
- Averages: every average is a sum divided by the count of requests that recorded the value, never an average of rows
- Model families: the top 5 by requests (DeepSeek, Qwen, Gemma, Mistral, GLM) are kept; the other 9 families, unnamed models and the long tail fold into Other
- Individual models: not shown; some names are anonymized ids, which aren't fit for a client page
- Model type "Unknown" (no signal in the model name): labelled "Unclassified"
- Destination: local page with DuckDB-WASM over a day × hour × family × model type × call type × streaming rollup (396K rows), since the 1.34M-row source has no use for the per-model grain here

## Data
- 1 row = day × trace hour × model family × model type × call type × streaming · 396,205 rows · 11 Apr 2025 – 12 Apr 2026 (367 days)
- Excluded: none (totals match the source: 6,122,413,756 requests)
- Requests = sum of requests (confirmed)
- Avg input tokens = input tokens / requests with a recorded input count; 7.5% of requests have none (assumed)
- Avg output tokens = output tokens / requests with a recorded output count (assumed)
- Avg time to first token = TTFT seconds / requests with a recorded TTFT; only streaming calls have one, 49% of requests (assumed)

## Story
1. KPIs: Requests = sum(requests) [compact]; Avg input tokens = ratio(input_tokens,input_n) [number]; Avg output tokens = ratio(output_tokens,output_n) [number]; Avg time to first token = ratio(ttft_seconds,ttft_n) [number]
2. "Requests peaked at 822M in September 2025, 2.4× May's 346M, then fell back" | trend | x=date:month y=sum(requests) color=family format=compact | brush
   > Monthly requests stacked by model family. The time strip in the transport bar brushes and plays every scene.
   ~ draw: reel 1/7 (family × month marks): stacked area, slices grow from the baseline left to right; instead of a line chart
   @ 2025-09-01: Peak month, 822M requests

3. "Model choice flipped: Qwen overtook DeepSeek in March 2026, 47% to 25%" | trend | x=date:month y=sum(requests) color=family format=percent | none
   > The same slices as shares of each month's requests.
   ~ draw: reel 2/7: the stacked area stretches to 100%
   @ 2026-03-01: Qwen takes first place

4. "In September 2025 Gemma carried 26% of requests, up from under 1% in June" | trend | x=date:month y=sum(requests) color=family format=percent | none
   > Each month as one 100% column.
   ~ draw: reel 3/7: the 100% area breaks into one 100% column per month
   @ 2025-09-01: Gemma at 26%

5. "Over the year, DeepSeek carried 55% of all 6.1B requests" | bar | category=family value=sum(requests) format=compact | click
   > Each month's column back on a request scale, stacked by family. Click a family anywhere to filter every scene; shift-click to add another.
   ~ draw: reel 4/7: the 100% columns drop to their true heights in requests

6. "DeepSeek's biggest month was June 2025 at 456M requests; Qwen's was January 2026 at 174M" | trend | x=date:month y=sum(requests) color=family format=compact | none
   > Each family on its own row, each month a column whose height is its requests. Drag to turn it; hover for values.
   ~ draw: reel 5/7: the stacked columns separate into rows and rise into 3D boxes (d3-3d), instead of a grouped bar chart

7. "Speed dipped and recovered; only GLM kept slowing, from 1.5 s to 6.7 s" | trend | x=date:month y=ratio(ttft_seconds,ttft_n) color=family format=number | none
   > The same family-months, now colored by average seconds to the first token (streaming calls only). Overall 2.9 s in May 2025 and 2.8 s in March 2026.
   ~ draw: reel 6/7: the boxes flatten into a family × month grid of heat cells, measure switches from requests to seconds
   @ 2025-09-01: Fastest month overall, 1.2 s

8. "GLM's first token reached 9.0 s in February 2026; no other family averaged above 4.2 s in any full month" | trend | x=date:month y=ratio(ttft_seconds,ttft_n) color=family format=number | none
   > Each family-month as a dot at its average seconds to the first token.
   ~ draw: reel 7/7: the heat cells shrink to dots and drop to their value on a seconds axis
   @ 2026-02-01: GLM at 9.0 s

9. "Every month's 24-hour profile is nearly flat: the day has no night" | trend | x=date:month y=sum(requests) color=hour format=compact | none
   > One ridge per month: requests by trace hour, each month on its own baseline.
   ~ draw: reel 1/2 (month × hour marks): ridgeline drawn top to bottom, instead of 24 lines

10. "In every month, the busiest trace hour carried at most 5.0% of that month's requests" | trend | x=date:month y=sum(requests) color=hour format=percent | none
   > The same profiles as small multiples on a shared scale of share of the month.
   ~ draw: reel 2/2: the ridges separate into a grid of panels on a shared percent scale

11. "Traffic is nearly flat around the clock" | bar | category=hour value=sum(requests) format=compact | none
   > Requests by trace hour over the whole period, as dots on a requests axis.
   ~ draw: reel 1/3 (hour marks): dot plot, instead of a bar chart

12. "The busiest hour carries 4.7% of traffic and the quietest 3.9%" | bar | category=hour value=sum(requests) format=compact | none
   > The same hours as bars from zero.
   ~ draw: reel 2/3: each dot stretches down into a zero-based bar

13. "Drawn as a clock, every hour is within 18% of every other" | bar | category=hour value=sum(requests) format=compact | none
   > The bars wrapped around a 24-hour dial; length from the inner ring is proportional and starts at zero.
   ~ draw: reel 3/3: the bars bend around the dial into radial bars

## Interaction
- Menus: model_type
- Detail table: no
- SQL on page: no
- Last updated: none

## Style
- register: formal
- density: balanced
- surface: stage
- focus: the selected model family
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
- data_character: time-heavy, categorical, anomaly-rich, sparse
- accent: #4e79a7
- alert: #e15759

## Data for the executor
```sql
COPY (
  SELECT DATE '2025-04-11' + dnum::INT AS date,
         hod::INT AS hour,
         CASE WHEN family IN ('DeepSeek','Qwen','Gemma','Mistral','GLM') THEN family ELSE 'Other' END AS family,
         CASE WHEN mtype = 'Unknown' THEN 'Unclassified' ELSE mtype END AS model_type,
         category AS call_type,
         streaming,
         sum(reqs)::BIGINT AS requests,
         sum(sum_it)::BIGINT AS input_tokens,  sum(n_it)::BIGINT AS input_n,
         sum(sum_ot)::BIGINT AS output_tokens, sum(n_ot)::BIGINT AS output_n,
         sum(sum_ttft) AS ttft_seconds,        sum(n_ttft)::BIGINT AS ttft_n
  FROM '../../../../../../kasivisu4.github.io/public/data/chutes/chutes.parquet'
  GROUP BY ALL
  ORDER BY date, hour
) TO 'traffic.parquet' (FORMAT parquet, COMPRESSION zstd)
```
