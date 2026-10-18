# D3 toolkit

What D3 (7.9.0) can do, one sentence each, so you know the vocabulary when you design. **This is a vocabulary, not a menu.** The best page usually combines pieces in a way no list names, or invents a form for this data's shape (`question-brief.md` §3, Concepts). Pick by what makes the finding obvious, never because something is listed here.

Full API docs: https://d3js.org/api. Mosaic still owns data and filtering: a D3 chart is a Mosaic client (`mosaic-tech.md`).

## Contents
- Data shaping
- Scales and color
- Shapes
- Layouts
- Interaction
- Motion
- Rendering
- Techniques worth knowing

## Data shaping (d3-array)

- **`d3.group` / `d3.rollup` / `d3.index`**: nest rows by keys into Maps (raw, reduced, or unique), the shape most layouts want.
- **`d3.bin`**: cut a numeric or date field into bins, for histograms, unit stacks and binned heatmaps.
- **`d3.quantile` / `d3.median` / `d3.extent` / `d3.deviation`**: summary statistics on the client, for reference lines and bands.
- **`d3.cumsum` / `d3.pairs` / `d3.rank` / `d3.least` / `d3.greatest`**: running totals, neighbours, ranks and extremes, for bump charts, slopes and annotations.
- **`d3.flatGroup` / `d3.cross`**: flat key combinations, e.g. to give every category × period a mark even where the data has none.

## Scales and color (d3-scale, d3-scale-chromatic)

- **Continuous** (`scaleLinear`, `scaleLog`, `scaleSqrt`, `scaleTime`/`scaleUtc`): map values to positions or sizes; `scaleSqrt` for areas, so area is proportional to value.
- **Discrete** (`scaleBand`, `scalePoint`, `scaleOrdinal`): categories to slots, positions or colors.
- **Binned** (`scaleQuantize`, `scaleQuantile`, `scaleThreshold`): continuous values to a few classes, for legible heatmaps and choropleths.
- **Sequential / diverging** (`scaleSequential`, `scaleDiverging` with `interpolateViridis`, `interpolateRdBu`…): magnitude, or distance from a meaningful midpoint.
- **`d3.interpolateLab` / `interpolateHcl`**: blend two colors perceptually, for custom ramps from theme colors.

## Shapes (d3-shape)

- **`d3.line` / `d3.area`** with **curves** (`curveMonotoneX` keeps extremes honest; `curveBumpX` for rank charts; `curveStep` for discrete changes; `curveCatmullRom` for gentle paths that still pass through the points).
- **`d3.stack`** with **orders and offsets** (`stackOffsetExpand` for 100%, `stackOffsetWiggle` for streams, `stackOffsetDiverging` for positive/negative): layered areas or bars.
- **`d3.arc` / `d3.pie`**: wedges, rings and radial bars; `padAngle` and `cornerRadius` for polish.
- **`d3.lineRadial` / `d3.areaRadial`**: lines and areas around a circle, for genuinely cyclic data.
- **`d3.link` / `linkHorizontal` / `linkRadial`**: smooth connectors, for trees, flows and annotations.
- **`d3.symbol`**: small glyphs (circle, cross, diamond, star…), a second categorical channel beside color.

## Layouts

- **Hierarchy** (`d3.hierarchy` → `tree`, `cluster`, `treemap`, `pack`, `partition`): part-whole and nesting as node-link trees, nested rectangles, nested circles, icicles or sunbursts.
- **Force** (`d3.forceSimulation` with `forceX`, `forceY`, `forceCollide`, `forceManyBody`, `forceLink`, `forceRadial`, `forceCenter`): a physics simulation that positions marks by attraction and collision, for beeswarms, clustered bubbles, networks and units regrouping between categories.
- **Chord** (`d3.chord`, `d3.ribbon`): flows between categories in a circle.
- **Delaunay / Voronoi** (`d3.Delaunay`, `voronoi`): nearest-point regions, for fast hover on dense marks and organic tessellations.
- **Contours and density** (`d3.contours`, `d3.contourDensity`): iso-lines of a grid or of point density, for terrain-like views of 2D distributions.
- **Geo** (`d3.geoPath` with projections such as `geoEqualEarth`, `geoAlbersUsa`, `geoOrthographic`): maps; projections can be interpolated into each other.
- **Plugins outside core** (load only when needed): d3-sankey for flow diagrams, d3-3d for projecting 3D shapes to SVG, flubber for morphing unlike shapes, d3-annotation for callouts.

## Interaction

- **`d3.brush` / `brushX` / `brushY`**: drag to select a range or box; feed it to a Mosaic clause.
- **`d3.zoom`**: pan and zoom with wheel, drag and pinch, with constrained extents; semantic zoom changes detail as the scale changes.
- **`d3.drag`**: move marks or rotate a 3D view by hand.
- **`d3.quadtree`**: find the nearest mark to the pointer fast, for tooltips on thousands of points.
- **`d3.pointer` / `d3.pointers`**: pointer and touch positions relative to a chart.

## Motion (d3-transition, d3-interpolate, d3-ease, d3-timer)

- **`selection.transition()`** with **`.join(enter, update, exit)`** and a **key function**: object constancy, so each datum keeps its mark and moves instead of being redrawn.
- **`.delay()` / chained `.transition()`**: stagger and stage changes; `transition.end()` returns a promise for sequencing scenes.
- **`attrTween` / `styleTween` / `tween`**: custom interpolation for path shapes, numbers counting up, text, and anything else.
- **`d3.interpolate*`**: numbers, colors, arrays, objects, transforms, path strings and dates, plus `interpolateZoom` for smooth camera moves (pan and zoom together, van Wijk & Nuij).
- **Easing** (`easeCubicInOut`, `easeQuadInOut`, `easeSinInOut`, `easeExpOut`, `easeLinear`…): the feel of motion; never back, elastic or bounce on values.
- **`d3.timer` / `d3.interval` / `d3.now`**: frame-synced loops for simulations, gliding playheads and canvas animation.

## Rendering

- **SVG**: crisp, inspectable, easy events; comfortable up to a few thousand marks.
- **Canvas** (D3 shapes accept a `context`): one bitmap redrawn per frame, for tens of thousands of marks or heavy animation; pair with a quadtree or Voronoi for hover.
- **WebGL** (three.js, regl): GPU drawing for very many marks or true 3D.
- **Hybrid**: canvas or WebGL marks under an SVG layer for axes, labels and hit targets.

## Techniques worth knowing

Each is one approach in a sentence; combine and adapt freely.

- **Unit visualization:** one mark per unit (a day, a request bucket, 1%), so totals are counts you can see, and units can fly from one grouping to another.
- **Force regrouping:** run `forceSimulation` with `forceX`/`forceY` targets per group and `forceCollide`, then change the targets to make the units split, merge or sort, physically and continuously.
- **Polygon morphing:** give every shape the same number of points and interpolate them (`show-reel.md`), or use flubber when shapes differ wildly, so any chart can turn into any other.
- **Staged transitions:** split a big change into short overlapping steps (move, then resize, then recolor), after Heer & Robertson's "Animated Transitions in Statistical Data Graphics".
- **Object constancy:** key every mark by its datum so filters and re-sorts move marks instead of replacing them.
- **Camera moves:** animate the viewport (`interpolateZoom`, or a d3-3d rotation) instead of the data, to guide attention to a region.
- **Scrollytelling:** scenes triggered by scroll position (IntersectionObserver), with the chart pinned while the text scrolls.
- **Animated time:** a playhead that glides through time, re-querying as it moves (`motion.md`, Glide).
- **Small multiples with shared scales:** one chart repeated per category, for comparisons without overplotting.
- **Annotation layers:** callouts, rules and labels as their own layer, computed from the data shown, so they stay true under filters.
- **Semantic zoom:** show aggregates when zoomed out and individual marks when zoomed in.
- **Brushing and linking:** a selection in one view filters or highlights every other (Mosaic does the linking).
- **Hover with Voronoi or quadtree:** nearest-mark tooltips that work on tiny or overlapping marks.
- **FLIP / View Transitions API:** animate DOM layout changes (cards reordering, panels resizing) by measuring first and last positions.
- **Physical metaphors:** gravity, flow, stacking, filling, erosion; motion that maps to what the data means (growth rises, churn drains).
- **Generative ornament from data:** textures, glyph fields or rhythm patterns driven by the data itself, decorative only where they never claim a value.
