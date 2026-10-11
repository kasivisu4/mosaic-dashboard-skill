# Mosaic + DuckDB-WASM engine

## Contents
- How the page works
- CONFIG (what build_page.py writes)
- Serving
- Extending the engine
- Troubleshooting

## How the page works

`assets/mosaic-dashboard.html` is a single HTML file with no build step:

1. Loads Mosaic vgplot `0.31.0` as an ES module from jsDelivr. Keep the version pinned; Mosaic's API changes between minor versions.
2. Starts DuckDB in the browser (`new vg.DuckDBWASMConnector()`) and loads each data file into a table (`vg.loadParquet` / `loadCSV` / `loadJSON`, with absolute URLs).
3. Each chart and menu publishes to its own `vg.Selection.single()`. One page-wide `vg.Selection.crossfilter({ include: own })` collects them. Marks and KPIs use it as `filterBy`, so they're filtered by every other chart's choice but never their own.
4. Bars highlight from their chart's own selection (`vg.highlight({ by: $own })`). Never highlight from the page-wide filter: other charts' predicates can't be evaluated on an aggregated mark, and DuckDB rejects the query.
5. Filter chips listen to each chart's own selection. A selection relays to the page filter *before* updating itself, so listening on the page filter reads stale values.
6. KPI tiles are `vg.MosaicClient` subclasses returning a one-row aggregate query. Each KPI has a filtered client and an unfiltered one for the "of N total" line.
7. All aggregation runs in DuckDB, so the page stays fast on millions of rows.

## CONFIG

`scripts/build_page.py` writes it from the plan; the vocabulary matches plan format v1.

```js
const CONFIG = {
  title: "…", takeaway: "…",
  data: [{ table: "orders_clean", url: "orders_clean.parquet" }],   // first = default table
  kpis: [{ label: "Revenue", value: "sum(revenue)", format: "currency" }],
  charts: [{ title: "…", form: "trend", keys: { x: "order_date:week", y: "sum(revenue)" }, interaction: "brush", note: "" }],
  menus: ["store"], detailTable: true,
  sql: { "<chart title>": "SELECT …" },                                // shown under each chart when non-empty
  style: { accent: "#2f6fde", alert: "#c2410c", currency: "USD" },
  buildNote: "<full plan text>",
};
```

Charts with `keys.from` set to another data file render unfiltered (their columns differ from the default table).

## Serving

```bash
python -m http.server 8000
```

Run it in the folder with `index.html` and the data files, then open `http://localhost:8000/`. The first load downloads the DuckDB engine (about 35 MB) from the CDN; after that the browser caches it.

## Extending the engine

Add a branch to `buildChart()` for a new form, keeping these rules:
- Read data with `vg.from(table, { filterBy: $filter })`.
- Publish interactions to the chart's own selection `$own` (passed in), never to `$filter`.
- Highlight only by `$own`.
- Add the form to `references/plan-format.md` and `plan_format.py` in the planner first (then run `tools/sync_plan_format.py`), so plans can ask for it.

Useful vgplot pieces: `vg.dot`, `vg.rectY` + `vg.bin`, `vg.barY`, `vg.intervalXY`, `vg.toggleX`, `vg.colorLegend({ as: $own })`, `vg.search({ from, column, as })`. Docs: https://idl.uw.edu/mosaic/

## Troubleshooting

| Symptom | Cause and fix |
|---|---|
| "must be served over http" | Opened from disk. Serve the folder. |
| Stuck on "Loading data…" | A data file isn't next to `index.html`. Check the Network tab for a 404. |
| `Binder Error: column "x" not found` | The plan names a column that isn't in the file. Re-run the planner's `validate_plan.py`. |
| `must appear in the GROUP BY clause` | Something highlights or filters an aggregated mark by another chart's column. Highlight only by `$own`. |
| Chart never filters | Its mark isn't using `filterBy: $filter`, or its interactor isn't publishing to its entry in `own`. |
| Chip lags one step behind | The chip listener is on `$filter`; listen on each `own` selection. |
| KPI shows `–` | The aggregate returned null; check the value expression (e.g. `sum` needs a numeric column). |
