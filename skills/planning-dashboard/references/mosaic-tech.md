# The tech: Mosaic + DuckDB-WASM + Observable Plot (+ D3)

There is no page template and no fixed layout. Design each dashboard for its data and its story: pick the marks, the composition, how numbers are shown, where filters live. The plan fixes *what* the page says (titles, order, metrics, notes) and *how it behaves and feels* (interaction rules, Style Profile); everything else is open. Prefer the chart that makes the finding obvious over a familiar one: small multiples, a heatmap of weekday × hour, a slope chart, a dot plot with a target rule, a raster of millions of points, an annotated timeline, a ranked table with inline bars.

This file is what you need to know to build it correctly.

## Contents
- Stack and imports
- Start DuckDB and load data
- Cross-filtering: the one pattern to get right
- What Observable Plot (vgplot) can draw
- Interactors and inputs
- Your own clients: HTML numbers, lists, D3 charts
- Pitfalls we've hit
- Check before sharing

## Stack and imports

Pin these versions; they're tested together.

```js
import * as vg from "https://cdn.jsdelivr.net/npm/@uwdata/vgplot@0.31.0/+esm";               // Plot marks, interactors, inputs, and Mosaic core re-exported
import { clausePoints, clauseInterval } from "https://cdn.jsdelivr.net/npm/@uwdata/mosaic-core@0.31.0/+esm"; // only for custom (D3/HTML) selections
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7.9.0/+esm";                              // only if Plot can't draw it
```

vgplot and mosaic-core share one module instance (same coordinator, same `Selection` class), so custom clients and vgplot charts can share selections. One HTML file next to the data files, served over http (`python -m http.server`); a page opened from disk can't load its data.

## Start DuckDB and load data

```js
vg.coordinator().databaseConnector(vg.wasmConnector());
await vg.coordinator().exec([
  vg.loadParquet("t", new URL("data.parquet", location.href).href),   // DuckDB-WASM needs absolute URLs
]);                                                                  // also vg.loadCSV, vg.loadJSON
const rows = (await vg.coordinator().query("SELECT max(d) AS last FROM t")).toArray(); // one-off values for titles, stamps
```

Load the full row-level file the plan exported, not pre-aggregated JSON: cross-filtering needs rows.

## Cross-filtering: the one pattern to get right

Give **every** interactive chart or input its **own** selection, and relay all of them into one page-wide crossfilter. Everything reads the page filter; each chart highlights by its own selection.

```js
const $page = vg.Selection.crossfilter();
const own = () => { const s = vg.Selection.single(); s._relay.add($page); return s; };
// _relay is what Selection.crossfilter({ include: [a, b] }) uses; this form lets you add charts one by one.
// If you know all selections up front, use: const $page = vg.Selection.crossfilter({ include: [a, b, c] });

const $cat = own();
vg.plot(
  vg.barX(vg.from("t", { filterBy: $page }), { x: vg.sum("amount"), y: "category", sort: { y: "-x" } }),
  vg.toggleY({ as: $cat }),
  vg.highlight({ by: $cat }),          // highlight by OWN selection, never by $page
);
```

Why: the crossfilter drops a chart's own clause from its filter, so the chart you click stays whole and every other chart and number follows. Highlighting by `$page` instead breaks aggregated marks (DuckDB "GROUP BY" errors).

Reset: call `reset()` on each own selection. Chips: listen on each own selection's `"value"` event (it fires after relaying, so the value is current) and describe `selection.value` in words.

## What Observable Plot (vgplot) can draw

Every mark takes `vg.from(table, { filterBy })` and channels that are column names or SQL aggregates, computed in DuckDB:
- **Marks:** `barX/barY`, `rectX/rectY` (histograms with `vg.bin(col)`), `lineX/lineY`, `areaX/areaY`, `dot`, `circle`, `text`, `tickX/tickY`, `ruleX/ruleY`, `cell`, `link`, `arrow`, `frame`, `regressionY`, `densityY`, `density`, `contour`, `heatmap`, `raster`, `hexbin`, `geo`, `errorbarX/Y`.
- **Aggregates and transforms:** `vg.count()`, `vg.sum`, `vg.avg`, `vg.median`, `vg.quantile`, `vg.min/max`, `vg.argmax`, `vg.bin`, `vg.dateMonth`, `vg.dateMonthDay`, `vg.dateDay`; any SQL via ``vg.sql`date_trunc('week', ${vg.column("d")})` ``.
- **Literal data** for annotations: `vg.ruleX([{ x: new Date("2025-12-29") }], { x: "x" })`, `vg.text([...], { x, text, frameAnchor: "top" })`.
- **Composition:** several marks in one `vg.plot`, `vg.hconcat` / `vg.vconcat` for linked layouts, `fx`/`fy` channels for small multiples.
- **Attributes:** `vg.width`, `vg.height`, margins, `vg.xTickFormat("$~s")`, `vg.yGrid(true)`, `vg.colorScheme`, `vg.colorDomain`/`colorRange`, `vg.style({...})`, `vg.xDomain(vg.Fixed)` to stop axes jumping while filtering.
- Docs and examples: https://idl.uw.edu/mosaic/api/vgplot/marks.html and https://idl.uw.edu/mosaic/examples/

## Interactors and inputs

| Interactor | Does | Note |
|---|---|---|
| `intervalX` / `intervalY` | brush a range; the page updates **live while dragging** | pass `field` when the axis is a computed expression (see Pitfalls) |
| `intervalXY` | brush a box | `xfield`, `yfield` |
| `toggleX` / `toggleY` / `toggleColor` / `toggle({channels})` | click to select values, shift-click adds | pair with `highlight({ by: own })` |
| `nearestX` / `nearestY` | select the value under the pointer (hover-driven) | good for linked rules/tooltips |
| `region` | brush selects the marks inside it as points | |
| `highlight` | dims what isn't selected | style with `fill`, `fillOpacity`, `opacity` |
| `panZoom`, `panZoomX` | pan/zoom; share a selection to link plots | |

Brush options: `brush: { fill, fillOpacity, stroke }` for its look; `pixelSize` to coarsen for huge data. Brushes signal the coordinator on pointer-enter so DuckDB pre-aggregates; keep them on row-level tables to get that speed.

Inputs (all take `from`, `as` an own selection, and `filterBy: $page` so their options follow the other filters): `vg.menu({ column })`, `vg.search({ column, type: "contains" })`, `vg.slider({ column })`, `vg.table({ from, filterBy, height })` for a live detail table.

## Your own clients: HTML numbers, lists, D3 charts

Anything not drawn by Plot (a headline number, a sentence that updates, a ranked list, a D3 chart) is a Mosaic client: it says what query it needs and redraws when the filter changes.

```js
class Live extends vg.MosaicClient {
  constructor(filterBy, query, render) { super(filterBy); this.q = query; this.r = render; }
  query(where = []) { return this.q(where); }
  queryResult(data) { this.r(data.toArray().map((d) => ({ ...d }))); return this; }
  queryError(e) { console.error(e); return this; }
}
const q = (where) => vg.Query.from("t").select({ v: vg.sql`avg(CAST(flag AS DOUBLE))` }).where(where);
vg.coordinator().connect(new Live($page, q, ([r]) => (el.textContent = fmt(r.v))));        // filtered
vg.coordinator().connect(new Live(undefined, q, ([r]) => (totalEl.textContent = fmt(r.v)))); // unfiltered total
```

A D3 chart that should filter the page selects through its own selection:

```js
const $mine = own();
const client = new Live($page, query, draw);  // draw(rows) renders with d3
const opts = { source: client, clients: new Set([client]) };   // clients = who is exempt from this filter
$mine.update(clausePoints(["category"], [["A"], ["B"]], opts)); // click: values
$mine.update(clauseInterval("d", [lo, hi], opts));             // brush: range (null clears)
```

## Pitfalls we've hit

- **Computed x axis + brush:** with `x: vg.sql\`date_trunc(...)\`` the brush filters on Plot's internal name `x`, which no other query has → "column x not found". Brush the real column: `intervalX({ as, field: "order_date" })`.
- **Highlight by the page filter** → GROUP BY errors on aggregated marks. Always `highlight({ by: ownSelection })`.
- **`Selection.crossfilter({ include })` only takes selections that exist when it's created**; relay later ones with `s._relay.add($page)` as above.
- **A client meant to be unfiltered** (a total): call `super(undefined)`. If your constructor gives `filterBy` a default value, passing `undefined` silently picks up that default and the "total" follows the filters.
- **Arrow values:** dates from `date_trunc` arrive as epoch milliseconds; wrap with `new Date(v)` for formatting. Wrap rows with `{ ...row }` before keeping them.
- **Don't pre-aggregate into the HTML** or embed JSON: it kills cross-filtering. Load the exported file.
- **Plotly or Chart.js** report a drag only on release and have no link to DuckDB; they can't do live crossfilter. Use Plot, or D3 through a client.
- **Width:** Plot doesn't resize itself; pass `vg.width(container.clientWidth)` and rebuild on resize if the layout is fluid.

## Check before sharing

Serve the folder and open it. Data loads, every chart and number renders, no console errors. Then use it as the reader would: drag each brush (other charts and numbers change *during* the drag), click each clickable chart, change each input, read the chips, press Reset. Fix anything that doesn't match the plan's interaction rules before giving the person the link.
