// dashboard-kit.js: Mosaic + DuckDB-WASM for data and cross-filtering, Observable Plot (via Mosaic's
// vgplot) for drawing, D3 for anything Plot can't draw. Copy this file next to the page and import it:
//   import * as kit from "./dashboard-kit.js";
//
// How the filtering works:
// - Every chart, menu and search box writes to its OWN selection. Each own selection relays into one
//   page-wide crossfilter, `filter`. Charts, KPIs and tables read `filter`, so a chart's own click or
//   brush filters everything else but never the chart itself; the chart highlights its choice instead.
// - Brushes are Mosaic's own interval interactors: they update the page live while you drag, and they
//   tell the coordinator a drag is coming so DuckDB can pre-aggregate and keep brushing fast on big data.

import * as vg from "https://cdn.jsdelivr.net/npm/@uwdata/vgplot@0.31.0/+esm";
import { clausePoints, clauseInterval } from "https://cdn.jsdelivr.net/npm/@uwdata/mosaic-core@0.31.0/+esm";

export { vg };

/** The page-wide filter. Pass `filterBy: kit.filter` to anything that should follow the filters. */
export const filter = vg.Selection.crossfilter();

const owners = []; // { selection, name, dates } per chart or input, for chips and Reset
const onChange = new Set(); // filter-bar renderers, told about every own selection whenever it's created

/** A selection for one chart or input, relayed into the page filter. */
function own(name, dates = false) {
  const selection = vg.Selection.single();
  // Same as Selection.crossfilter({ include: [...] }), which only takes selections known up front.
  selection._relay.add(filter);
  owners.push({ selection, name, dates });
  // Listen on the own selection: it updates after relaying to `filter`, so its value is current.
  selection.addEventListener("value", () => onChange.forEach((f) => f()));
  onChange.forEach((f) => f());
  return selection;
}

const css = (name) => getComputedStyle(document.documentElement).getPropertyValue(name).trim();
/** A SQL snippet from the plan, e.g. "sum(revenue)" or "avg(CAST(returned AS DOUBLE))". */
const raw = (text) => vg.sql([text]);
const rowsOf = (data) => (typeof data?.toArray === "function" ? data.toArray().map((r) => ({ ...r })) : data ?? []);
const widthOf = (el) => Math.max(260, Math.floor(el.clientWidth || el.parentElement?.clientWidth || 480));

// ---------- start ----------

/** Start DuckDB in the browser and load data files as tables: start({ orders: "orders.parquet" }). */
export async function start(tables) {
  if (location.protocol === "file:") {
    throw new Error("Serve this folder over http to load its data, e.g.  python -m http.server 8000  then open http://localhost:8000/");
  }
  vg.coordinator().databaseConnector(vg.wasmConnector());
  const loaders = { parquet: vg.loadParquet, csv: vg.loadCSV, json: vg.loadJSON };
  await vg.coordinator().exec(Object.entries(tables).map(([table, file]) => {
    const load = loaders[file.split(".").pop().toLowerCase()];
    if (!load) throw new Error(`Can't load ${file}: use .parquet, .csv or .json`);
    return load(table, new URL(file, location.href).href); // DuckDB-WASM fetches by absolute URL
  }));
}

/** Run one query and get plain rows back (for titles, notes and stamps computed once). */
export async function rows(query) {
  return rowsOf(await vg.coordinator().query(query));
}

// ---------- formats ----------

let currency = "USD";
export function setCurrency(code) { currency = code; }

/** format(value, "currency" | "compact" | "percent" | "number" | "exact") */
export function format(v, kind = "number") {
  if (v == null || Number.isNaN(Number(v))) return "–";
  const opts = {
    currency: { style: "currency", currency, notation: "compact", maximumFractionDigits: 1 },
    compact: { notation: "compact", maximumFractionDigits: 1 },
    percent: { style: "percent", maximumFractionDigits: 1 },
    exact: { maximumFractionDigits: 6 },
    number: { maximumFractionDigits: 2 },
  }[kind] ?? { maximumFractionDigits: 2 };
  return new Intl.NumberFormat(undefined, opts).format(Number(v));
}
// d3-format specifiers for axes, matching format() above.
const AXIS = { currency: "$~s", compact: "~s", percent: ".0%", number: "~s", exact: "," };

// ---------- custom clients (KPIs, lists, D3) ----------

class Client extends vg.MosaicClient {
  // filterBy: null means "ignore the filters" (used for unfiltered totals).
  constructor({ filterBy = filter, query, render }) {
    super(filterBy ?? undefined);
    this._query = query;
    this._render = render;
  }
  query(where = []) { return this._query(where); }
  queryResult(data) { this._render(rowsOf(data)); return this; }
  queryError(err) { console.error(err); return this; }
}
const connect = (client) => (vg.coordinator().connect(client), client);

/**
 * kpi(el, { table, label, value: "sum(revenue)", format, target, direction })
 * The filtered value, with the unfiltered total under it. Off-target values get the breach color.
 * direction: "up-good" | "down-good" (needed with a target).
 */
export function kpi(el, { table, value, label = value, format: kind = "number", target, direction }) {
  el.classList.add("kpi");
  el.innerHTML = `<div class="kpi-label"></div><div class="kpi-value">…</div><div class="kpi-total"></div>`;
  el.querySelector(".kpi-label").textContent = label;
  const q = (where) => vg.Query.from(table).select({ v: raw(value) }).where(where);
  connect(new Client({
    query: q,
    render: ([r]) => {
      const out = el.querySelector(".kpi-value");
      out.textContent = format(r?.v, kind);
      const off = target != null && r?.v != null && (direction === "down-good" ? r.v > target : r.v < target);
      out.classList.toggle("breach", off);
      out.title = target != null ? `Target ${direction === "down-good" ? "≤" : "≥"} ${format(target, kind)}` : "";
    },
  }));
  connect(new Client({ filterBy: null, query: q, render: ([r]) => { el.querySelector(".kpi-total").textContent = `of ${format(r?.v, kind)} total`; } }));
}

/**
 * exceptions(el, { table, category, value, above | below, format })
 * The categories past a limit, worst first, as a short table. Follows the filters; says so when empty.
 */
export function exceptions(el, { table, category, value, above, below, format: kind = "number" }) {
  const limit = above ?? below;
  const cmp = above != null ? ">" : "<";
  el.classList.add("exceptions");
  connect(new Client({
    query: (where) => vg.Query
      .from(vg.Query.from(table).select({ k: vg.column(category), v: raw(value), n: vg.count() }).where(where).groupby(category))
      .select("*").where(vg.sql`v ${raw(cmp)} ${vg.literal(limit)}`).orderby(raw(above != null ? "v DESC" : "v ASC")),
    render: (list) => {
      if (!list.length) { el.innerHTML = `<p class="muted">Nothing past the limit (${cmp} ${format(limit, kind)}).</p>`; return; }
      el.innerHTML = `<table><thead><tr><th></th><th class="num">Value</th><th class="num">Rows</th></tr></thead><tbody></tbody></table>`;
      el.querySelector("tbody").append(...list.map((r) => {
        const tr = document.createElement("tr");
        tr.innerHTML = `<td></td><td class="num breach"></td><td class="num"></td>`;
        tr.children[0].textContent = r.k;
        tr.children[1].textContent = format(r.v, kind);
        tr.children[2].textContent = format(r.n, "compact");
        return tr;
      }));
    },
  }));
}

/**
 * custom(el, { query: (where) => Query, render: (rows, el, api) => void, name })
 * Draw with D3 (or anything) and still take part in the page filter.
 * api.selectPoints(field, values) and api.selectInterval(field, [lo, hi] | null) filter the page;
 * api.selected() is this chart's current choice, for highlighting.
 */
export function custom(el, { query, render, name = "Chart", filterBy = filter }) {
  const selection = own(name);
  const api = {};
  const client = connect(new Client({ filterBy, query, render: (r) => render(r, el, api) }));
  const opts = { source: client, clients: new Set([client]) };
  api.selectPoints = (field, values) => selection.update(clausePoints([field], values?.length ? values.map((v) => [v]) : null, opts));
  api.selectInterval = (field, range) => selection.update(clauseInterval(field, range, opts));
  api.selected = () => selection.valueFor(client) ?? null;
  return client;
}

// ---------- Observable Plot charts (vgplot) ----------

const brushStyle = () => ({ fill: css("--selected"), fillOpacity: 0.18, stroke: css("--selected") });
const common = (el, height) => [
  vg.width(widthOf(el)), vg.height(height),
  vg.style({ color: css("--ink"), fontFamily: css("--font") || "system-ui, sans-serif", fontSize: "12px", background: "transparent" }),
];

/**
 * bar(el, { table, category, value: "sum(revenue)", limit: 10, format, name, interactive })
 * Ranked horizontal bars. Click filters the page, shift-click adds; the rest of the bars dim.
 */
export function bar(el, { table, category, value, limit = 10, format: kind = "number", name = category, interactive = true }) {
  const sel = interactive ? own(name) : null;
  el.replaceChildren(vg.plot(
    vg.barX(vg.from(table, { filterBy: filter }), { x: raw(value), y: category, fill: css("--focus"), sort: { y: "-x", limit } }),
    ...(sel ? [vg.toggleY({ as: sel }), vg.highlight({ by: sel, fill: css("--ink-muted"), fillOpacity: 1 })] : []),
    vg.xLabel(null), vg.yLabel(null), vg.xGrid(true), vg.xTickFormat(AXIS[kind]), vg.marginLeft(110),
    ...common(el, Math.max(140, 26 * limit + 30)),
  ));
}

/**
 * trend(el, { table, date, bucket: "week", value, format, name, annotations: [{ x: "2025-12-29", text }] })
 * A line over time, drawn point to point. Drag across it to filter the page to a date range (live).
 */
export function trend(el, { table, date, bucket = "week", value, format: kind = "number", name = date, annotations = [], interactive = true }) {
  const sel = interactive ? own(name, true) : null;
  const x = vg.sql`date_trunc(${vg.literal(bucket)}, ${vg.column(date)})`;
  const notes = annotations.map((a) => ({ x: new Date(a.x), text: a.text }));
  el.replaceChildren(vg.plot(
    vg.lineY(vg.from(table, { filterBy: filter }), { x, y: raw(value), stroke: css("--focus"), strokeWidth: 2 }),
    ...(notes.length ? [
      vg.ruleX(notes, { x: "x", stroke: css("--ink-muted"), strokeDasharray: "3,3" }),
      vg.text(notes, { x: "x", text: "text", frameAnchor: "top", dy: -8, fill: css("--ink"), fontSize: 11 }),
    ] : []),
    // Brush on the date column itself: the x channel is a computed bucket that only exists inside the chart's query.
    ...(sel ? [vg.intervalX({ as: sel, field: date, brush: brushStyle() })] : []),
    vg.xLabel(null), vg.yLabel(null), vg.yGrid(true), vg.yTickFormat(AXIS[kind]), vg.marginLeft(52), vg.marginTop(20),
    ...common(el, 240),
  ));
}

/**
 * histogram(el, { table, value: "revenue", format, name })
 * Distribution of one numeric column. Drag to filter the page to a range (live).
 */
export function histogram(el, { table, value, format: kind = "number", name = value, interactive = true }) {
  const sel = interactive ? own(name) : null;
  el.replaceChildren(vg.plot(
    vg.rectY(vg.from(table, { filterBy: filter }), { x: vg.bin(value), y: vg.count(), fill: css("--focus"), inset: 0.5 }),
    ...(sel ? [vg.intervalX({ as: sel, field: value, brush: brushStyle() })] : []),
    vg.xLabel(null), vg.yLabel("rows"), vg.yGrid(true), vg.xTickFormat(AXIS[kind]), vg.marginLeft(48),
    ...common(el, 220),
  ));
}

/**
 * scatter(el, { table, x, y, name })
 * Points; drag a box to filter the page by both columns (live).
 */
export function scatter(el, { table, x, y, name = `${x} × ${y}`, interactive = true }) {
  const sel = interactive ? own(name) : null;
  el.replaceChildren(vg.plot(
    vg.dot(vg.from(table, { filterBy: filter }), { x, y, fill: css("--focus"), fillOpacity: 0.4, r: 2 }),
    ...(sel ? [vg.intervalXY({ as: sel, xfield: x, yfield: y, brush: brushStyle() })] : []),
    vg.xLabel(x), vg.yLabel(y), vg.grid(true), vg.marginLeft(52),
    ...common(el, 280),
  ));
}

// ---------- filters ----------

/** menu(el, { table, column, label }): a dropdown of the column's values. Its options follow the other filters. */
export function menu(el, { table, column, label = column }) {
  el.append(vg.menu({ from: table, column, label, as: own(label), filterBy: filter }));
}

/** search(el, { table, column, label }): a text box that keeps rows whose column contains the text. */
export function search(el, { table, column, label = column }) {
  el.append(vg.search({ from: table, column, label, type: "contains", as: own(label), filterBy: filter }));
}

/** detailTable(el, { table, height }): the rows that match the filters. */
export function detailTable(el, { table, height = 320 }) {
  el.append(vg.table({ from: table, filterBy: filter, height }));
}

/** Filter chips ("Store: East") and a Reset button. Can be placed before or after the charts. */
export function filterBar(el) {
  const chips = Object.assign(document.createElement("div"), { className: "chips" });
  const reset = Object.assign(document.createElement("button"), { type: "button", textContent: "Reset" });
  el.append(chips, reset);
  const day = new Intl.DateTimeFormat(undefined, { month: "short", day: "numeric", year: "numeric" });
  const text = (v, dates) => {
    if (v == null || v === "") return null;
    if (Array.isArray(v) && v.length === 2 && !Array.isArray(v[0])) {
      return v.map((x) => (dates || x instanceof Date ? day.format(new Date(x)) : format(x))).join(" – ");
    }
    if (Array.isArray(v) && Array.isArray(v[0]) && v[0].length === 2 && !Array.isArray(v[0][0])) {
      return v.map((r) => r.map((x) => format(x)).join(" – ")).join(" × ");
    }
    return Array.isArray(v) ? v.flat().join(", ") : String(v);
  };
  const render = () => {
    const active = owners.map((o) => [o, text(o.selection.value, o.dates)]).filter(([, t]) => t);
    chips.replaceChildren(...(active.length
      ? active.map(([o, t]) => Object.assign(document.createElement("span"), { className: "chip", textContent: `${o.name}: ${t}` }))
      : [Object.assign(document.createElement("span"), { className: "muted", textContent: "No filters" })]));
    reset.disabled = !active.length;
  };
  onChange.add(render);
  reset.addEventListener("click", () => { owners.forEach((o) => o.selection.reset()); render(); });
  render();
}
