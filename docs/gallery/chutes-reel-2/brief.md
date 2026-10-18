# Brief: a year of LLM traffic, as a poster

## Reader
- Who: client-side readers (product and engineering leads at companies that build on hosted open models) who know what tokens and time to first token are, but have never seen this platform's traffic. *(inferred from "clients")*
- What: how request volume, token usage, latency and model choice changed over one year of traffic, and what the daily usage pattern looks like.
- Why: to judge which open model families real traffic is moving to, and what load and latency look like through a day. A shift in model choice matters more to them than raw volume. *(inferred)*
- How: opened once, explored for a few minutes on a laptop, with individual scenes screenshotted into decks; so every scene must be true on its own, with its period and units on it.
- Hook: model choice flipped. DeepSeek served 84.4% of requests in May 2025 (first full month) and 24.8% in March 2026 (last full month); Qwen went from 5.3% to 47.0% over the same months. Over the whole trace DeepSeek still served 54.9% of 6.12B requests. (queries in `3-layout/layout.md`)

## Supporting questions
1. Who served the traffic over the whole year? (lens: composition)
   - Answer preview: DeepSeek 54.9% of 6.12B requests; DeepSeek and Qwen together 69.9%.
   - Comparison: each family's part of the whole year.
   - Visual: a single 100% bar that breaks into a treemap of all 14 families instead of a pie, because one length and then areas are read exactly; the treemap keeps the small families visible.
   - Motion: segments of the bar split into treemap tiles (same marks, area = requests).
   - Honesty check: rule 3, areas proportional to values (treemap area = requests).
2. How did model choice move month by month? (lens: change, rank)
   - Answer preview: Qwen grew from 0.60M to 5.05M requests a day (May 2025 → March 2026) while DeepSeek fell from 9.42M to 2.67M; Qwen's share 5.3% → 47.0%; by tokens DeepSeek fell from 92.2% to 21.8%.
   - Comparison: family × month, first and last full months.
   - Visual: heat cells that rise into 3D bars, then fall into stacked bars, 100% stacked bars and a 100% token-share area, instead of a multi-line chart, because the same 78 marks show level, volume and share in turn.
   - Motion: one set of family-month marks morphs through five forms (show reel).
   - Honesty check: rule 9, partial months (Apr 2025: 20 days, Apr 2026: 12 days) are drawn as requests per day and labelled partial.
3. How did volume move? (lens: change)
   - Answer preview: 11.2M requests a day in May 2025, a 27.4M peak in September, 10.7M in March 2026.
   - Comparison: per-day volume by month, peak named as a peak.
   - Visual: stacked bars of requests per day, built from the family marks, instead of a line.
   - Motion: the 3D boxes settle onto the floor as stacked columns.
   - Honesty check: rule 8, the title names the September peak as a peak and compares full months.
4. Does latency follow the daily load? (lens: relationship, rhythm)
   - Answer preview: 13:00 on the trace clock carries 18.5% more requests than 22:00; time to first token is slowest at 11:00 (2.50 s) and fastest at 23:00 (2.08 s).
   - Comparison: hour by hour, volume then latency on the same 24 marks.
   - Visual: hour bars that shrink into a dot plot of time to first token, instead of a dual-axis line.
   - Motion: bars collapse to dots on a new axis (measure changes with the axis label).
   - Honesty check: rule 4, one measure per axis; the axis and title change together.
5. Did the daily rhythm change during the year? (lens: rhythm, contrast)
   - Answer preview: the busiest hour was 1.14× the quietest in May 2025 and 1.33× in March 2026; 12:00–17:00 carried 26.1% of May's requests and 28.7% of March's; the busiest hour fell between 12:00 and 15:00 in 10 of 11 full months.
   - Comparison: month × hour.
   - Visual: small-multiple day curves that slide into a ridgeline and then a heatmap, instead of 12 overlaid lines.
   - Motion: curve slices drop into overlapping rows, then square up into cells.
   - Honesty check: rule 5, shared y-scale across the small multiples (stated).

## Angles not drawn
- Distribution of days (quietest day 2026-01-13 at 1.64M requests, slowest day 2026-02-27 at 5.32 s): histograms are removed for client audiences by the style system; the quiet day is named in the technical notes instead.
- Streaming vs non-streaming and request category: Chat is 86% of requests, so the split says little; left to the technical notes.

## Limitations
- Time to first token exists only for requests with `n_ttft` > 0 (streaming requests); non-streaming requests have none, so latency describes streamed traffic only.
- The hour is the trace clock's hour; the timezone is not stated in the data.
- No cost, error or user data: the trace can't say why families rose or fell.
