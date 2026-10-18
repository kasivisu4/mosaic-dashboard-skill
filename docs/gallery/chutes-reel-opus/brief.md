# Brief: a year of LLM traffic on Chutes

## Reader
- Who: client-side readers (partners, customers, people evaluating open-model serving) who know what an LLM request, a token and time-to-first-token are, but have never seen this platform's traffic. *(inferred from audience = clients)*
- What: "How did request volume, token usage, latency and model choice change over a year of production LLM traffic, and what usage patterns sit inside it?"
- Why: to understand which open-model families real traffic actually runs on, and how fast that choice moves. A wholesale change of the model everyone uses would matter more to them than raw volume. *(inferred)*
- How: opened once from a shared file, explored for a few minutes on a laptop screen; individual scenes screenshotted into decks. Must read without a presenter.
- Hook: **the handover.** DeepSeek served 84.4% of requests in May 2025 and 24.8% in March 2026, while Qwen went from 5.3% to 47.0% (first and last full months; explore round 2, "family share per full month").

## Concepts considered (for the hook)
Seed provocations: "one mark is one unit; totals are counts you can see" and "marks regroup physically between scenes, never fading out and in".
1. Bump chart of family rank by month: honest and readable, but the rank hides the size of the swing (84% → 25% looks like "1st → 2nd"), and it is a catalog form.
2. 100% stacked monthly columns with direct labels: the clearest reading of share, but by itself a stock chart. Kept as the landing view of the hook, reached by a morph.
3. 3D skyline of family × month × requests a day: striking, three real axes, but the share is hard to read in perspective. Kept as a later scene, not the hook.
4. Waffle per month (100 squares = 100%): honest units, but 13 waffles side by side are busy, and the units carry no volume.
5. **Invented: the bead abacus.** One bead = 10 million requests (613 beads for the year after per-month rounding). Each month is an abacus rod; its beads stack up from the floor in family order, so the rod's height is the month's volume and the colours are its mix. The same beads then roll off their rods into one heap per family, so the year's totals are bead counts you can see, and back. The reader sees DeepSeek's blue fill the early rods and Qwen's orange take over the late ones before reading a number.
Chosen: 5 opens the page (volume and mix at once, countable, unseen in a dashboard) and 2 lands the hook's exact numbers one act later; together they pass all three tests: obvious in five seconds (the colour flips across the rods), honest (bead counts are rounded totals, stated on the chart and in every tooltip; rods start at the floor; partial months are marked), and new to the reader.

## Supporting questions
1. When did the handover happen, and was it a drift or a step? (lens: change, rank)
   - Answer preview: DeepSeek fell from 9.4M to 2.7M requests a day while Qwen rose from 0.6M to 5.1M (May 2025 → Mar 2026); Qwen's share jumped from 8.0% in Nov to 23.4% in Dec 2025, then passed DeepSeek in Mar 2026 (47.0% vs 24.8%).
   - Comparison: family against family, month by month, in absolute requests a day and in share.
   - Visual: per-family small-multiple bars on a shared scale, morphing into 100% stacked columns, instead of a multi-line chart; the morph shows that the share view is the same cells.
   - Motion: the cells slide from their family panels into stacked columns (staged: move, then resize).
   - Honesty check: rule 9 (partial periods): April 2025 and April 2026 are partial; their columns are hatched and labelled, and every per-day figure divides by the days present.
2. How big was the traffic, and when did it peak? (lens: change, distribution)
   - Answer preview: 6.12 billion requests; 11.2M a day in May 2025, peaking at 27.4M a day in September 2025 (2.45×), back to 10.7M a day in March 2026. The busiest day, 29 Oct 2025, had 34.9M; 13 Jan 2026 recorded only 1.6M (3 of 24 hours).
   - Comparison: month against month; day against day.
   - Visual: the bead abacus instead of monthly columns; a day strip (one dot per day) instead of a daily line.
   - Motion: beads stack up rod by rod; the days drift from their rods' positions into the strip.
   - Honesty check: rule 11 (missing data is a gap): the 13 Jan near-outage is annotated as incomplete hours, not a demand drop.
3. Did latency improve as volume grew? (lens: relationship)
   - Answer preview: average time to first token was 2.93 s in May 2025, fell to 1.23 s in September 2025 and rose back to 2.80 s by March 2026; within DeepSeek alone it went 3.02 → 1.56 → 3.34 s (first full month, fastest month, last full month), so it is not only the model mix.
   - Comparison: the same family × month cells, re-coloured by a new measure.
   - Visual: heat cells of TTFT by family × month instead of a line per family.
   - Motion: the share columns spread back into a family × month grid and re-colour (axis and legend change with them).
   - Honesty check: rule 10 (denominator): TTFT is a ratio of sums over streaming calls only; the legend and tooltips say so and give the call count.
4. Is there a daily or weekly rhythm? (lens: rhythm)
   - Answer preview: weak. Wednesdays average 7.2% more requests than Saturdays (52 full weeks); the busiest trace hour (13) has only 1.19× the requests of the quietest (22); but TTFT does follow the clock, 2.50 s at hour 11 vs 2.08 s at hour 23.
   - Comparison: weekday against weekday; hour against hour.
   - Visual: a weekly spiral of days instead of a weekday bar chart; hour bars that bend into a 24-hour radial clock instead of a line.
   - Motion: the day strip winds into a spiral; the hour bars bend into a ring.
   - Honesty check: rule 7 (radial forms): angle is used only for cyclic hour and weekday; radial bar length is linear from an inner ring; the trace clock is labelled as the trace's own hour, not local time.
5. What does a request look like in tokens? (lens: composition)
   - Answer preview: 6,321 input tokens and 445 output tokens per request on average (14.2 input tokens per output token).
   - Comparison: input against output, filtered against all.
   - Visual: KPI numbers with their unfiltered totals, not a chart.
   - Motion: count-up on load and on every filter.
   - Honesty check: rule 10: averages are ratios of sums (sum_it / n_it, sum_ot / n_ot).

## Angles not drawn
- The reasoning wave (reasoning models 17.1% → 44.7% peak in Nov 2025 → 7.2% in Mar 2026): a strong finding, but it needs a model-type dimension the stage would add as a third categorical axis; mentioned in the technical notes instead.
- Model fragmentation (effective number of models 2.2 → 11.6): model-level data (201 ids, many raw UUIDs) is not exported; families carry the story.
- Streaming vs non-streaming split: no story beyond "TTFT exists only for streaming calls".

## Limitations
- The trace's hour (`hod`) is the trace clock, not a known time zone; hour patterns are relative.
- Token counts exist only for text endpoints (9.1% of rows have none); TTFT only for streaming calls (42.3% of rows have none).
- Requests are counts from the operator's logs; the data says nothing about users, prices or quality.
- 13 Jan 2026 (3 of 24 hours) and 14 Jan 2026 (15 hours) are incomplete days.
