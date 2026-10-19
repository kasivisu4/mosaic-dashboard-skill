---
plan_version: 2
goals: explore
audience: clients
cadence: one-time
review_depth: quick
success_criteria: "map level interactive: the map is the control surface; brushing it filters every other view"
reconcile: false
destination: file
source: ../../../../kasivisu4.github.io/public/data/nyc-trips.parquet
data:
  - file: trips.parquet
    rows: 999033
---

# A day of New York taxis

Nine in ten trips start within 4 miles of Times Square, but the airports earn almost three times their share of the fares. The city's centre rides at lunchtime, and the rings around it ride after midnight.

## Assumptions
- Format: one-page story (stage), 10 scenes in 4 acts, laid out as the seed's scrolly-split
- Coordinates: New York State Plane Long Island, US feet (ESRI:102718), checked against Times Square and JFK
- Exclusions: trips with a pickup or drop-off outside x 900,000–1,070,000 ft and y 110,000–280,000 ft are dropped (967 trips, 0.1%)
- Zones: straight-line rings around Times Square (under 1, 1–2, 2–4, 4–8, 8+ miles) by pickup point; JFK and LaGuardia boxes count as "Airport" first
- Airport trip: pickup or drop-off inside the JFK or LaGuardia box
- Hour: the hour of day the trip started, pooled over every day in the file (the file has no dates)
- Zero-mile trips (7,429), 7 duplicate rows and 1 zero-rider trip are kept and noted
- Interaction: the map's box brush is the one brush; the hour clock is the one click chart; Play sweeps a 3-hour window
- Map form: the plan format has no map form and clients pages may not use scatter, so the map is written as a zone bar; its ~ draw line is the real instruction (density raster of px, py with a box brush on pickup location)
- Colors: one hue per zone from the seed's palette, with the airports in gold as the hook's color; blue focus, orange-red alert

## Data
- 1 row = one taxi trip · 999,033 rows · time of day only, no dates
- Excluded: 967 trips with an out-of-area pickup or drop-off (coordinates of 0 or far outside New York)
- Trips = count of trips (assumed)
- Fares = sum of fare in USD (assumed)
- Average fare = sum of fare / trips (assumed)
- Average trip = sum of distance in miles / trips (assumed)
- Airport share of fares = fares of airport trips / all fares, under the current filter (assumed)
- Zone = ring around Times Square by straight-line distance from the pickup point, airports first (assumed)

## Story
1. KPIs: Trips = count() [compact]; Fares = sum(fare) [currency]; Average fare = avg(fare) [currency]; Average trip = avg(distance) [number]
2. "93.2% of 999,033 pickups start within 4 miles of Times Square" | bar | category=zone value=count() | click
   > Every pickup in the file, binned to the pixel. Hover to look through the lens at where trips that start there end; drag a box to filter every scene.
   ~ draw: density raster map of every pickup (x=px, y=py, box brush on pickup location) with a where-to lens (inside it the drop-offs of trips that began there) instead of a choropleth of zones, 1M exact points need no borders we don't have
   @ Under 1 mi: Times Square
3. "Of every 100 pickups, 3 start at JFK or LaGuardia" | bar | category=zone value=count() | none
   > One square is 1% of the pickups in view.
   ~ draw: waffle of 100 squares grown out of the shrinking map instead of a pie, counts not angles
   @ Airport: 2.8% of trips
4. "Count dollars instead of trips and the airports take 8 of every 100" | bar | category=zone value=sum(fare) | none
   > Same 100 squares, now 1% of fares each; squares change zone as the measure switches.
   ~ draw: the same waffle re-dealt by fare share instead of a second pie, the gold block triples in place
   @ Airport: 8.1% of fares
5. "Airport pickups earn 2.9× their share of trips" | bar | category=zone value=sum(fare) | none
   > Squares are fares; the outline on each row is that zone's share of trips.
   ~ draw: unit bars, one row of squares per zone with a ghost outline of its trip share, instead of a grouped bar, the gap between square and outline is the story
   @ Airport: 2.9× trip share
6. "Midnight is the busiest hour: 67,964 trips, 4.7× the 6 a.m. low" | bar | category=hour value=count() | click
   > The day as a clock: each wedge's length from the inner ring is the hour's trips. Click an hour to filter; Play sweeps the hand.
   ~ draw: radial bars on a 24-hour dial instead of a line chart, the day is a cycle and midnight sits beside 11 p.m.
   @ 0: Busiest hour
   @ 6: Quietest hour
7. "6 a.m. trips are the longest: 4.64 miles on average, twice 7 p.m.'s 2.31" | bar | category=hour value=avg(distance) | click
   ~ draw: the dial unrolls into straight bars (same 24 marks, new measure) instead of a dual-axis chart, one measure per view
   @ 6: Longest trips
8. "At 8 a.m., trips to or from an airport earn 32.8% of the hour's fares" | bar | category=hour value=ratio(airport_fare,fare) format=percent | click
   > Dot: airport share of the hour's fares. Tick: their share of the hour's trips.
   ~ draw: bars shrink into a dot plot with a trip-share tick per hour instead of a stacked bar, the gap between tick and dot is the airport premium
   @ 8: Peak airport share
9. "Within a mile of Times Square trips peak at 1 p.m.; 1–4 miles out they peak at midnight and 1 a.m." | bar | category=zone value=count() | none
   > Rows are zones, columns are hours, darker is more trips.
   ~ draw: zone × hour heatmap (the 2D view the terrain rises from) instead of a grouped bar
   @ Under 1 mi: Peak at 1 p.m.
10. "The highest point is the 1–2 mile ring at midnight: 23,871 trips" | bar | category=zone value=count() | none
   > Drag to turn the terrain. Height and color both show trips.
   ~ draw: the heatmap's cells rise into a 3D terrain of zone × hour × trips (d3-3d boxes, height linear from zero) instead of a static heatmap
   @ 1–2 mi: Highest point
11. "4–8 miles out, 9.5% of the day's trips start in the 1 a.m. hour, the sharpest peak of any ring" | bar | category=zone value=count() | none
   > Each line is one zone's day as a share of its own trips, so shapes compare despite different sizes.
   ~ draw: the terrain falls flat and its columns slide into small-multiple lines, one panel per zone on a shared share scale, instead of an overlaid multi-line
   @ 4–8 mi: Sharpest peak

## Interaction
- Menus: none
- Detail table: no
- SQL on page: no
- Last updated: none

## Style
- register: formal
- density: balanced
- surface: stage
- focus: airport trips
- color_mode: categorical
- direction: none
- type_scale: standard
- interaction: light
- motion: reveal
- chart_set: KPIs, bar
- anomalies: explain
- narrative: captions
- provenance: footnote
- numbers: rounded
- data_character: anomaly-rich, ordinal
- accent: #4269d0
- alert: #ff725c
- currency: USD

## Data for the executor
```sql
COPY (
  SELECT
    CAST(floor("time") AS TINYINT) AS hour,
    CAST(round(px/50)*50 AS INTEGER) AS px, CAST(round(py/50)*50 AS INTEGER) AS py,
    CAST(round(dx/50)*50 AS INTEGER) AS dx, CAST(round(dy/50)*50 AS INTEGER) AS dy,
    CAST(distance AS FLOAT) AS distance, CAST(fare AS FLOAT) AS fare, riders,
    CASE WHEN (px BETWEEN 1035000 AND 1056000 AND py BETWEEN 160000 AND 185000) OR (px BETWEEN 1012000 AND 1026000 AND py BETWEEN 216000 AND 228000) THEN 'Airport'
         WHEN sqrt((px-988267)^2+(py-215437)^2)/5280 < 1 THEN 'Under 1 mi'
         WHEN sqrt((px-988267)^2+(py-215437)^2)/5280 < 2 THEN '1–2 mi'
         WHEN sqrt((px-988267)^2+(py-215437)^2)/5280 < 4 THEN '2–4 mi'
         WHEN sqrt((px-988267)^2+(py-215437)^2)/5280 < 8 THEN '4–8 mi'
         ELSE '8+ mi' END AS zone,
    CAST(((px BETWEEN 1035000 AND 1056000 AND py BETWEEN 160000 AND 185000) OR (px BETWEEN 1012000 AND 1026000 AND py BETWEEN 216000 AND 228000)
       OR (dx BETWEEN 1035000 AND 1056000 AND dy BETWEEN 160000 AND 185000) OR (dx BETWEEN 1012000 AND 1026000 AND dy BETWEEN 216000 AND 228000)) AS TINYINT) AS airport,
    CAST(CASE WHEN (px BETWEEN 1035000 AND 1056000 AND py BETWEEN 160000 AND 185000) OR (px BETWEEN 1012000 AND 1026000 AND py BETWEEN 216000 AND 228000)
       OR (dx BETWEEN 1035000 AND 1056000 AND dy BETWEEN 160000 AND 185000) OR (dx BETWEEN 1012000 AND 1026000 AND dy BETWEEN 216000 AND 228000) THEN fare ELSE 0 END AS FLOAT) AS airport_fare
  FROM 'C:/Users/kasiv/projects/kasivisu4.github.io/public/data/nyc-trips.parquet'
  WHERE px BETWEEN 900000 AND 1070000 AND py BETWEEN 110000 AND 280000
    AND dx BETWEEN 900000 AND 1070000 AND dy BETWEEN 110000 AND 280000
) TO 'trips.parquet' (FORMAT parquet, COMPRESSION zstd, COMPRESSION_LEVEL 19)
```
