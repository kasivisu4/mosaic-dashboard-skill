# Brief: a year of LLM traffic

## Reader
- Who: client-side readers who know LLMs but not this platform's traffic *(inferred from audience = clients)*
- What: how request volume, token usage, latency, model selection and usage patterns changed over the year
- Why: to judge where LLM usage is heading: which model families are winning, whether prompts are growing, whether serving got faster *(inferred)*
- How: opened once and explored for a few minutes; individual charts likely screenshotted into decks, so each must be true on its own *(inferred from one-time + clients)*
- Hook: model choice flipped (and September 2025 was the odd month, with volume, speed and prompt size all swinging together). DeepSeek held 87.9% of requests in June 2025; by March 2026 Qwen led with 47.0% to DeepSeek's 24.8% (monthly share by family)

## Supporting questions
1. When did the lead change hands, and who else rose and fell? (lens: rank)
   - Answer preview: Qwen took first place in March 2026; Gemma briefly reached 26.0% in September 2025, then fell back to ~2%
   - Comparison: each family's rank, month by month
   - Visual: bump chart of monthly rank with share labels, instead of a multi-line of requests (lines tangle; the crossings are the story)
   - Motion: lines draw left to right on reveal; the play button moves a highlight month by month
   - Honesty check: rule 9, the first and last months are partial (from 11 Apr 2025, to 12 Apr 2026); marked on the axis

2. How big was each family over the selection? (lens: composition)
   - Answer preview: DeepSeek 54.9% of the year, Qwen 15.0%, Other 16.7%, Gemma 5.6%, Mistral 4.2%, GLM 3.6%
   - Comparison: part to whole
   - Visual: waffle of 100 squares (1 square = 1%), instead of a pie or a ranked bar; clicking a family filters the page
   - Motion: squares re-sort into their new counts when the filter changes
   - Honesty check: rule 1 (counts, not angles); rounding uses largest remainders so it always shows exactly 100

3. Was the September peak real growth or one family? (lens: change)
   - Answer preview: volume rose from 7.5 M requests a day (Apr 2025) to 27.4 M (Sep 2025), back to 10.7 M (Apr 2026); one outage day, 13 Jan 2026, at 1.6 M
   - Comparison: day by day across the year
   - Visual: slim context strip with a brush along the top, instead of a full-height line chart (it's the page's time control, and it drives every other view)
   - Motion: transitions on every filter; the play button moves a 4-week window across it
   - Honesty check: rule 8, the full year is shown by default; rule 11, the outage is shown as the dip it is

4. Did serving get faster or slower, and are prompts growing? (lens: change + composition)
   - Answer preview: over full months, neither moved much (first token 2.9 s in May 2025, 2.8 s in March 2026; prompts 6.9K to 7.4K tokens). September was the outlier (1.2 s, 4.2K tokens) as Gemma carried 26% of requests with 0.8 s and 536-token prompts. Only GLM kept slowing, 1.5 s (July) to 6.7 s (March).
   - Comparison: family × month for latency; first vs last full month per family for prompt size
   - Visual: heat strips (family × month, value in each cell) for latency, and a log-scale slope chart for prompt size, instead of two average lines
   - Motion: cells sweep in month by month; slope lines grow left to right
   - Honesty check: rule 8, endpoints are the first and last full months, never a peak or low. An earlier draft said latency "nearly tripled" (September low vs partial April) and prompts "doubled after September"; both were artifacts of the starting point and were rewritten.

5. Is there a daily rhythm? (lens: rhythm)
   - Answer preview: almost none. The busiest trace hour carries 4.7% of requests, the quietest 3.9%
   - Comparison: 24 hours of the cycle
   - Visual: radial 24-hour clock, instead of a 24-bar chart (a cycle drawn as a cycle)
   - Motion: bars grow from zero on reveal; transition on filter
   - Honesty check: rule 7, bar length from the inner ring is proportional to requests, starting at zero, so the flatness is shown truthfully; hours are labelled "trace hour" (no known timezone)

## Angles not drawn
- Connected scatter of volume against latency: the client audience removes scatter, and the mix confound would make it easy to over-read. Its finding goes in the caption of angle 4.
- Calendar heatmap of daily volume: it would be a seventh chart, past the density cap; the strip already shows the peak and the outage.

## Limitations
- Individual models (some are anonymized ids) and per-request latency distributions aren't in the rollup.
- Hours are on the trace's own clock, so "time of day" can't be read as local business hours.
