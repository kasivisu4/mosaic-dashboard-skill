# Brief: New York taxi trips, one day in the life

## Reader
- **Who:** clients or external readers who know New York by name but have never seen this trip data. They don't know what the columns mean, and they shouldn't have to.
- **What:** "Build an interactive dashboard" from the trip file: show what's interesting, with the **map as the thing you interact with** (success criterion: "map level interactive").
- **Why:** to explore where and when the city takes taxis and where the money is. The surprise is that a small set of trips (the airports) carries an outsized share of the fares, and that the centre and the rings around it keep different hours. *(inferred)*
- **How:** opened once and explored for several minutes on a laptop screen. The reader steps through scenes, brushes the map, hovers to look closer, and takes screenshots for a deck. *(inferred)*
- **Hook:** JFK and LaGuardia pickups are **2.8% of trips but 8.1% of fares**. At 8 a.m., trips touching an airport are 12.4% of the hour's trips and **32.8% of its fares**. (From `explore.md` round 3 and round 4, after exclusions.)

## Concepts considered (for the hook)
1. **Density raster of every pickup**: 1M points binned to pixels, so the streets draw themselves. This is the map itself, and it is honest and instant to read, but on its own it shows *where*, not the money.
2. **Bullseye of rings around Times Square**: concentric annuli with area proportional to trips, plus an airport satellite circle. It is clear, but abstract: it throws the actual map away.
3. **Clock of 24 mini-maps**: a small multiple of maps around a dial. It is striking, but each map is tiny and unreadable at laptop size.
4. **Waffle of 100 squares, trips then fares**: the same squares regroup when the measure switches from trips to fares, and the airport row triples. This makes the hook's ratio obvious.
5. **Invented, the "where-to lens"**: hovering the pickup map shows a lens. Under it, the map switches to the **drop-offs of trips that started inside the lens**, with a counter of how many trips and what share of fares. Pointing at JFK lights up all of Manhattan. This is a hidden layer revealed by the pointer (seed provocation 2), and no catalog names it.

**Chosen:** 5 on top of 1 for the opening scene, because the map is the control surface the reader asked for and the lens lets them discover the airport effect with their own hand. 4 then states the hook as numbers two scenes later. 2 and 3 are dropped (abstract, or unreadable at size).

## Supporting questions
1. **Where do trips start?** (lens: distribution / contrast)
   - Answer preview: 93.2% of pickups start within 4 miles of Times Square.
   - Comparison: inside the ring vs outside; pickups vs the drop-offs revealed by the lens.
   - Visual: a density raster with the where-to lens, **instead of** a choropleth or pin map, because 1M exact points need no zone boundaries we don't have.
   - Motion: the raster fades in; the lens follows the pointer; the map shrinks into the corner of the stage when the reader moves on and stays there as the filter.
   - Honesty check: rule 11 (missing ≠ zero) and color scale. The color ramp uses a log scale, labelled "log scale", with a legend; out-of-view trips are counted and noted, never dropped silently.
2. **Where is the money?** (lens: composition)
   - Answer preview: airport pickups are 2.8% of trips and 8.1% of fares.
   - Comparison: share of trips vs share of fares, by pickup zone.
   - Visual: **waffle → unit bars → unit bars by fares**, instead of a pie or stacked bar, because each square is 1% and the reader counts the airport row growing from 3 to 8.
   - Motion: squares regroup from the waffle into rows, then hop between rows when the measure switches to fares.
   - Honesty check: rule 10 (shares show their denominator). Each scene says "1 square = 1% of trips (or fares) in view", and the tooltip gives the exact count and total.
3. **When does the city ride?** (lens: rhythm)
   - Answer preview: midnight is the busiest hour (68,019 trips), 4.7× the 6 a.m. low (14,369).
   - Comparison: hour against hour, around the clock.
   - Visual: **radial bars on a 24-hour dial**, instead of a line chart, because the day is a cycle and midnight sits next to 11 p.m., not at the far edge.
   - Motion: wedges grow from the inner ring; a playhead hand sweeps the clock on Play.
   - Honesty check: rule 7 (radial). Hour is cyclic; wedge length is linear from the inner ring, and the ring is labelled as zero.
4. **Which hours make the long, lucrative trips?** (lens: change within the cycle / relationship)
   - Answer preview: 6 a.m. trips average 4.65 mi, twice 7 p.m.'s 2.31 mi. At 8 a.m., airport trips earn 32.8% of the hour's fares.
   - Comparison: the same 24 hours, measure switched (trips → miles → airport fare share).
   - Visual: the dial **unrolls into straight bars** (miles), then the bars **shrink into a dot plot** (airport share), instead of a dual-axis line chart, because one measure per view keeps every axis honest.
   - Motion: wedges unroll into bars (same 24 marks), then bars collapse to dots.
   - Honesty check: rule 4 (one axis per measure) and rule 1 (bars from zero). The dot plot's axis is a position scale starting at 0%.
5. **Do the centre and the rings keep different hours?** (lens: contrast)
   - Answer preview: within 1 mile of Times Square trips peak at 1 p.m.; 1–2 miles out they peak at midnight, and 2–4 miles out at 1 a.m.
   - Comparison: zone × hour.
   - Visual: **heatmap → 3D terrain → small-multiple lines**, instead of a plain heatmap. The terrain shows the whole surface (the midday hump in the centre, the night ridge in the rings); the lines make each zone's shape comparable.
   - Motion: cells rise out of the heatmap into boxes (camera tilts), then fall flat and slide into per-zone line panels.
   - Honesty check: rule 3 / stage §5. Three data axes; height is linear from zero; color repeats height; exact values on hover; the lines panel uses each zone's share of its own day, labelled "share of the zone's trips".

## Angles not drawn
- **Riders per trip**: 57.5% carry one rider, and average fares barely differ by group ($10.75–$11.29). Nothing to see, so it is left out.
- **Fare per mile**: it rises from $3.30 at 6 a.m. to $4.24 at 7–8 p.m. It is real but subtle. It goes in the tooltips of the hour marks instead of its own scene.
- **The fare-cent pattern** (night surcharge visible in the cents): interesting, but it needs fare-rule knowledge we can't confirm from the file.

## Limitations
- There are no dates, so trends across days, weekdays or seasons can't be shown. "Hour" pools every day in the file.
- There are no borough or zone boundaries. Zones are straight-line rings around Times Square plus two airport boxes, an approximation that is labelled on the page.
- There are no tips, payment types or trip ids.
