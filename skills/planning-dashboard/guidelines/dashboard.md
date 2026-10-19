# Dashboard guideline

> **Customize this file** for your organization. It sets the technology pages are built with, the interaction every page must have, and your color policy. It deliberately doesn't set a layout. How a page's style is *chosen* from goal, audience and data is method, in `references/style-system.md`; you shouldn't need to edit that. Rules here can tighten the defaults, never loosen them.

## Build stack

| Part | Use | Why |
|---|---|---|
| Data and filtering | **Mosaic** (`@uwdata/mosaic-core` 0.31.0) with **DuckDB-WASM** in the browser | every chart, number and input queries DuckDB; one cross-filter links them |
| Charts | **Observable Plot** through Mosaic's vgplot (`@uwdata/vgplot` 0.31.0) | Mosaic's own brushes and clicks: live updates while dragging, pre-aggregation for big data |
| Anything Plot can't draw, and every animated chart | **D3** (`d3` 7.9.0) as a Mosaic client | still joins the same cross-filter; keyed transitions, staged reveals and a time player (`references/motion.md`) |
| 3D that morphs with 2D (three data axes only) | **d3-3d** (`d3-3d` 1.0.0) projecting boxes to SVG polygons | 3D forms join the polygon morph engine (`references/show-reel.md` §5) |
| 3D with thousands of marks | **three.js** (`three` 0.160.0) as a Mosaic client | GPU instancing; orbit camera; heights tweened with D3 (`references/stage.md` §5) |
| Icons | **Tabler icons** webfont (`@tabler/icons-webfont` 3.35.0) | scene markers, controls, category chips, KPI labels; never a quantity (`references/show-reel.md` §6). The main stylesheet (`dist/tabler-icons.min.css`) has few `-filled` icons; for filled ones also load `dist/tabler-icons-filled.min.css` from the same package |

How to use them, with the pitfalls already found: `references/mosaic-tech.md`. There is **no page template**: each page is designed fresh for its data and story (layout, chart types, how numbers are shown). One HTML file next to the data while building (served over http for testing), shared as a single self-contained `report.html` (`scripts/bundle_report.py`) that needs no server. No other chart library (Plotly, Chart.js and similar can't brush live against DuckDB).

## Visual ambition

- **Out of the box, not off the shelf.** Every chart is chosen with `references/visual-language.md`: know the conventional form for the question, then draw something that shows the finding better (bump chart, waffle, beeswarm, horizon, calendar heatmap, connected scatter…). A conventional form is used only when nothing beats it, and its `~ draw:` line says why.
- **One hero, or one stage.** Each page opens on one large, animated primary surface (the brief's hook), with the supporting angles beneath it; with `impact`, prefer the one-screen stage (`surface: stage`, `references/stage.md`), whose marks morph through scenes.
- **A show reel, not a slideshow.** One set of marks morphs through each chain of forms the design seed picks (`references/show-reel.md`); a fresh seed every run, so no two dashboards look alike.
- **Motion on.** Default `motion: reveal` wherever the audience allows it: staged entrance in reading order, transitions on every filter, count-up numbers, a play button when the story is change over time.
- **Honest, always.** The honesty rules in `visual-language.md` Part 3 are never traded for style.

## Interaction must-haves

Whatever the design, every page that has interaction:
- Uses one page-wide filter that every chart, number, list and table follows.
- Never filters a chart by its own selection; the chart highlights its choice instead.
- Updates the page *while* a brush is dragged, not only on release.
- Shows what is filtered, in words ("Store: East"), with a visible Reset.
- Shows filtered numbers next to their unfiltered totals somewhere, so a filter's effect is visible.
- Marks any value past its target with the `breach` color.
- Gives every mark a tooltip with its exact values, and every title, KPI, control and legend help text (`references/interaction.md`, Tooltips and help).

How many controls a page has comes from the Style Profile's `interaction` level (`references/style-system.md`).

## Colors: suggested, not fixed

The planner **suggests** a palette for each dashboard from its Style Profile (`color_mode`, `direction`, `focus`, data character) using the roles in `references/style-system.md`, shows it on the confirmation card as an assumption the person can change, and writes it into the plan's `## Style` (`accent`, `alert`). Pages set each role as a CSS variable (e.g. `--focus`, `--breach`) with light and dark values.

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
- Number formats: thousands as 412K, millions as 2.1M; currency with its symbol; percentages with one decimal unless `numbers: exact`.
