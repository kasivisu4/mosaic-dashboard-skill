# Brief: LLM traffic story, one year

## Reader
- Who: Clients (external readers) who run or buy LLM serving and know the field but not this platform's trace *(inferred from audience = clients)*.
- What: How did request volume, token usage, latency and model choice change over the year of traffic?
- Why: To judge which model families the platform's traffic is moving toward, and what a year of use looks like for planning *(inferred)*.
- How: Opened once, scrolled and played through the story, then explored filters for a few minutes; screenshots may go into a client deck *(inferred)*.
- Hook: Qwen went from 5.3% of requests in May 2025 to 47.0% in March 2026, passing DeepSeek (which fell from 84.4% to 24.8%), while the monthly total stayed flat (346.2M to 333.1M). (computed: `sum(reqs)` by family and month, full months only)

## Supporting questions

1. Which families carry the traffic, and did the order change? (lens: Rank and Composition)
   - Answer preview: DeepSeek led every month until March 2026, when Qwen passed it (47.0% vs 24.8%).
   - Comparison: family rank by month (rank/time).
   - Visual: a bump chart of family ranks by month instead of a 100% stacked area, because the finding is the rank crossing, which a stacked area hides.
   - Motion: ranks slide between months during Play; the crossing is the moment that stops.
   - Honesty check: family grouping can shift with naming (Unnamed, Long tail); the page labels the grouping and shows that "Unnamed" changes.

2. When did Qwen's volume step up? (lens: Change)
   - Answer preview: Qwen went from 45.8M requests in November 2025 to 132.5M in December 2025 (step, not drift).
   - Comparison: Qwen volume, this month vs the month before.
   - Visual: a unit morph: each block is a million requests, so the step can be counted by eye; the conventional line would hide the scale.
   - Motion: blocks fill during Play.
   - Honesty check: the unit is stated; the axis starts at zero.

3. Does latency follow the mix, or does the mix only look like it does? (lens: Relationship)
   - Answer preview: TTFT by family over the full year: Qwen 2.02 s, DeepSeek 2.68 s; in December 2025 Qwen 1.19 s vs DeepSeek 2.50 s; monthly TTFT is noisy (1.23 s in September, 2.80 s in March).
   - Comparison: Qwen share (x) against all-traffic TTFT (y), one dot per month, connected in time order.
   - Visual: a connected scatter, path drawn in time order, instead of a line chart of two series, because the relation is the path.
   - Motion: the path draws month by month.
   - Honesty check: TTFT covers streaming calls only (n_ttft); the page says so and does not compare it to non-streaming traffic.

4. Is there a daily rhythm in traffic? (lens: Rhythm)
   - Answer preview: traffic peaks at hour 13 (285.6M requests) and bottoms at hour 05 (241.6M): an 18% swing, on the trace clock (timezone not in the file).
   - Comparison: hour of day against the average hour.
   - Visual: a radial clock of 24 hour segments, instead of a bar chart, because the cycle is the finding.
   - Motion: segments grow in hour order.
   - Honesty check: the trace clock's zone is unknown; the page says "trace clock", not local time.

5. Token usage: are calls getting longer or shorter? (lens: Change, with mix caveat)
   - Answer preview: average input tokens per call rose from 6,855 (May 2025) to 7,355 (March 2026); average output fell from 542 to 405.
   - Visual: a pair of small multiples with a shared axis; the averages are ratios of sums, so the page shows the totals next to them.
   - Honesty check: the average moves with the mix (streaming share fell 66% to 45%), so the page shows streaming and non-streaming apart or states the mix effect.

## Angles not drawn
- Distinct models per month (55 to 121 to 61): a count is not a shape worth its own form; it appears as one number in the explore section.
- Max-row token totals (13.6 billion input tokens in one row): true, but an outlier in the sums; it goes into the technical section, not a chart.
- Per-model detail for "Other models" (40% of requests): not decomposable in this file; left out.

## Limitations
- The file is rolled up to day and hour; per-request latency distribution (p50, p95) cannot be computed. TTFT is a mean of streaming calls only.
- sum_ttft units are not documented in the file; read as seconds.
- 13 Jan 2026 has 3 hours of data and 14 Jan has 15; January totals are understated by roughly 20M requests.
- The April 2025 and April 2026 months are partial; no "from X to Y" claim uses them.
- Family and model names are the trace's, with grouping columns (`g_family`, `g_model`) that can shift as names change.
- No cost or revenue data: the page shows volume, tokens and latency only.
