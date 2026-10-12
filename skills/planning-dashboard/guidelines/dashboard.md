# Dashboard guideline

> **Customize this file** for your organization. It sets how pages are built (the stack), how filtering and KPIs behave, and your color policy. How a page's style is *chosen* from goal, audience and data is method, in `references/style-system.md`; you shouldn't need to edit that. Rules here can tighten the defaults, never loosen them.

## Build stack

| Part | Use | Why |
|---|---|---|
| Data and filtering | **Mosaic** (`@uwdata/mosaic-core` 0.31.0) with **DuckDB-WASM** in the browser | every chart, KPI and input is a Mosaic client querying DuckDB; one cross-filter links them |
| Charts | **Observable Plot** through Mosaic's vgplot (`@uwdata/vgplot` 0.31.0) | Mosaic's own brushes and clicks: live updates while dragging, pre-aggregation for big data |
| Anything Plot can't draw | **D3** (`d3` 7.9.0) via `kit.custom()` | still joins the same cross-filter |
| Page code | `assets/dashboard-kit.js`, copied next to the page | the engine is tested once; each page only says what to draw |

Pages are one HTML file plus the kit and the data files, served over http. No other chart library.

## Cross-filtering

- One page-wide filter. Every chart, KPI, list and table follows it.
- A chart is never filtered by its own selection; it highlights it instead (selected marks keep their color, the rest dim).
- **Brush** (drag a range) on time, histogram and scatter charts; the page updates *while* dragging.
- **Click** on bars (shift-click adds, click again removes).
- Always a visible **Reset** and **filter chips** that say what is filtered in words ("Store: East").
- How many charts are interactive comes from the Style Profile's `interaction` level (`references/style-system.md`).

## Filters

- A **menu** for each dimension the reader would slice by, up to the density cap; its options follow the other filters.
- A **search** box instead of a menu when a dimension has more than 30 values.
- Filters sit in one bar above the KPIs, with the chips and Reset.
- A date range comes from brushing the trend, not a separate date picker.

## KPIs

- Each tile: label, the filtered value, and "of {total} total" underneath, so a filter's effect is visible.
- A KPI with a target names its direction (`up-good` or `down-good`); off-target values use the `breach` color, and the target shows on hover.
- At most the audience's KPI cap (`references/style-system.md`, Audience overrides).
- Number formats: thousands as 412K, millions as 2.1M; currency with its symbol; percentages with one decimal unless `numbers: exact`.

## Colors: suggested, not fixed

The planner **suggests** a palette for each dashboard from its Style Profile (`color_mode`, `direction`, `focus`, data character) using the roles in `references/style-system.md`, shows it on the confirmation card as an assumption the person can change, and writes it into the plan's `## Style` (`accent`, `alert`). The page sets each role as a CSS variable (`--ink`, `--ink-muted`, `--focus`, `--selected`, `--breach`, plus light and dark values).

Rules for a suggestion:
- Neutral grey ink; one focus hue; a breach hue that is clearly different from focus and readable by color-blind readers (blue focus with orange-red breach works; red with green doesn't).
- `selected` is never the same as `focus`.
- Categorical palettes: at most 6 hues, color-blind safe (e.g. Okabe–Ito or Tableau 10), the same category keeps its color on every chart.
- Text and marks meet WCAG AA contrast in both light and dark mode.

**Brand colors (optional).** If your organization must use fixed colors, pin them here and the planner uses them instead of suggesting. Leave the table empty to let it suggest.

| Role | Light | Dark |
|---|---|---|
| | | |

Fonts: the platform's sans (system-ui) for everything; a serif only for the headline and hero number when `register: editorial`; tabular figures for numbers, always.

## Audience limits (tighten only)

The defaults are in `references/style-system.md` (Audience overrides). Add stricter rules for your organization here, e.g.:

- leadership: at most 4 KPI tiles (default 5)
- clients: always show the organization's logo and a confidentiality footer

## House rules

- Never ask the person about chart library or styling; this file and the Style Profile decide. Colors are the exception: they're suggested on the card and the person may change them there.
