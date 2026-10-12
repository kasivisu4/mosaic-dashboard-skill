# Building the page

Build with the stack in `guidelines/dashboard.md`. Copy `assets/dashboard-kit.js` next to the plan and its data, then write `index.html` from the skeleton below. Don't rewrite the kit's engine in the page; if the plan needs something the kit doesn't draw, use `kit.custom()` with D3.

## Contents
- Plan to kit
- Page skeleton
- Colors and type from the Style Profile
- Check before sharing

## Plan to kit

| In the plan | Call |
|---|---|
| `source` / `data` files | `await kit.start({ <table>: "<file>.parquet" })` |
| KPI `Label = agg(col) [format] target<=N` | `kit.kpi(el, { table, label, value: "agg(col)", format, target: N, direction: "down-good" })` (`>=` is `up-good`) |
| `rate(flag)` | value `"avg(CAST(flag AS DOUBLE))"`, format `percent` |
| `count()` | value `"count(*)"` |
| `bar` · `category=c value=v` · `click` | `kit.bar(el, { table, category: "c", value: "v", format, name })` |
| `trend` · `x=date:bucket y=v` · `brush` | `kit.trend(el, { table, date: "date", bucket, value: "v", format, name, annotations })` |
| `@ date: text` under a chart | an entry in `annotations: [{ x: "date", text }]` |
| `histogram` · `value=col` · `brush` | `kit.histogram(el, { table, value: "col", format, name })` |
| `scatter` · `x=a y=b` · `brush` | `kit.scatter(el, { table, x: "a", y: "b" })` |
| `exceptions` · `category=c value=v above=N` | `kit.exceptions(el, { table, category: "c", value: "v", above: N, format })` |
| interaction `none` on a chart | add `interactive: false` |
| `> note` under a chart | a `<p class="note">` under its title |
| `Menus: a, b` | `kit.menu(filtersEl, { table, column: "a", label })` each; `kit.search` for > 30 values |
| `Detail table: yes` | `kit.detailTable(el, { table })` |
| `Last updated: col` | `kit.rows("SELECT max(col) AS last FROM <table>")` → "Last updated …" under the title |
| `SQL on page: yes` | a `<details><summary>SQL</summary><pre>…</pre></details>` under each chart |
| `currency` token | `kit.setCurrency("EUR")` before the KPIs |

Charts appear in the plan's story order. Each chart card: the finding-title as `<h2>`, then a hint ("Drag to filter" / "Click to filter, shift-click to add") when interactive, then the chart, then its note. The plan's takeaway goes under the page title.

## Page skeleton

```html
<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{plan title}</title>
<style>
  /* Suggested palette from the plan's ## Style (accent = --focus, alert = --breach). */
  :root { --bg: #f7f8fa; --card: #fff; --ink: #1f2933; --ink-muted: #9aa5b1; --grid: #e6e9ed;
          --focus: {accent}; --selected: {a hue distinct from focus}; --breach: {alert};
          --font: system-ui, -apple-system, "Segoe UI", sans-serif; }
  @media (prefers-color-scheme: dark) {
    :root { --bg: #111418; --card: #1a1f25; --ink: #e4e7eb; --ink-muted: #5f6b77; --grid: #2a3139;
            --focus: {lighter accent}; --selected: {lighter selected}; --breach: {lighter alert}; }
  }
  * { box-sizing: border-box; }
  body { margin: 0; background: var(--bg); color: var(--ink); font: 14px/1.5 var(--font); font-variant-numeric: tabular-nums; }
  main { max-width: 1180px; margin: 0 auto; padding: 24px 16px 48px; }
  h1 { font-size: 24px; margin: 0 0 4px; } .muted { color: var(--ink-muted); }
  .bar { display: flex; flex-wrap: wrap; gap: 12px; align-items: center; margin: 16px 0; }
  .chips { display: flex; gap: 6px; flex-wrap: wrap; }
  .chip { background: var(--card); border: 1px solid var(--grid); border-radius: 999px; padding: 2px 10px; font-size: 12px; }
  button, select, input { font: inherit; color: var(--ink); background: var(--card); border: 1px solid var(--grid); border-radius: 6px; padding: 4px 10px; }
  .kpis { display: grid; grid-template-columns: repeat(auto-fit, minmax(180px, 1fr)); gap: 12px; }
  .kpi, .card { background: var(--card); border: 1px solid var(--grid); border-radius: 10px; padding: 14px 16px; }
  .kpi-label { font-size: 13px; color: var(--ink-muted); } .kpi-value { font-size: 30px; font-weight: 600; } .kpi-total { font-size: 12px; color: var(--ink-muted); }
  .breach { color: var(--breach); }
  .grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(min(100%, 460px), 1fr)); gap: 12px; margin-top: 12px; }
  .card h2 { font-size: 15px; font-weight: 600; margin: 0 0 2px; } .hint, .note { font-size: 12px; color: var(--ink-muted); margin: 0 0 6px; }
  table { border-collapse: collapse; width: 100%; } th, td { text-align: left; padding: 6px 4px; border-bottom: 1px solid var(--grid); } .num { text-align: right; }
  footer { margin-top: 24px; font-size: 12px; color: var(--ink-muted); }
</style>
</head>
<body>
<main>
  <h1>{plan title}</h1>
  <p>{takeaway}</p>
  <p class="muted" id="updated"></p>
  <div class="bar" id="filters"></div>
  <section class="kpis"><div id="k1"></div><div id="k2"></div></section>
  <section class="grid">
    <article class="card"><h2>{finding-title}</h2><p class="hint">Drag to filter</p><div id="c1"></div><p class="note">{note}</p></article>
  </section>
  <footer>{provenance: source, definitions}</footer>
</main>
<script type="module">
  import * as kit from "./dashboard-kit.js";
  const $ = (id) => document.getElementById(id);
  const T = "{table}";
  await kit.start({ [T]: "{data file}" });
  kit.filterBar($("filters"));
  kit.menu($("filters"), { table: T, column: "{dimension}", label: "{Label}" });
  kit.kpi($("k1"), { table: T, label: "{Label}", value: "{agg(col)}", format: "{format}" });
  kit.trend($("c1"), { table: T, date: "{date col}", bucket: "{bucket}", value: "{agg(col)}", format: "{format}", name: "{Label}" });
</script>
</body>
</html>
```

## Colors and type from the Style Profile

- Set the CSS variables from the plan: `accent` → `--focus`, `alert` → `--breach`; pick `--selected` and the dark-mode values by the rules in `references/style-system.md` (Color system).
- `color_mode: status`: charts stay in `--focus`; only off-target KPIs and exceptions use `--breach`. `categorical`: pass a palette to Plot through `kit.vg` (e.g. `kit.vg.colorRange([...])`) only if categories repeat across charts.
- `type_scale`: change the KPI value and title sizes in the `<style>` block to the scale's sizes. `register: editorial`: a serif for `h1` and the hero KPI only.
- `provenance`: `footnote` → the footer; `inline` / `per-number` → a definition line under each KPI or chart title.
- `motion: none` → nothing extra (the kit doesn't animate).

## Check before sharing

Serve the folder (`python -m http.server 8000` in `4-dashboard/`) and open it. Confirm the data loads, every chart and KPI renders, and there are no console errors. Then drag a brush and click a bar: the other charts and the KPIs should change while dragging, the chips should name the filters, and Reset should clear them.
