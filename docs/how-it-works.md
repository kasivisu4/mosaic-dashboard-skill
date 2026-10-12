# How the skill works (plain-language guide)

This is for you, not for Claude. It isn't shipped with the skill.

## The big picture

There are two skills, and they do separate jobs:

1. **The planner** (`planning-dashboard`) figures out *who* will read the dashboard, *what* the data contains and means, and *what story* it should tell. It asks a few short questions where they matter, then writes everything down as a **plan** (`plan.md`) and checks the plan with a script.
2. **An executor** turns the plan into a dashboard. For now the planner does this itself: Claude designs and builds the page from the plan, fresh each time, with Mosaic, DuckDB and Observable Plot. Other executors can be added later (`building-dashboard-mosaic` is parked, or a company's BI system, or a person), because they only need the plan.

The plan is the handshake between the two. Its format is written down (`references/plan-format.md`), so anyone can build an executor without touching the planner.

## What each folder is for

| Folder / file | Plain meaning |
|---|---|
| `SKILL.md` | The "front page" Claude reads first. Its top lines (name + description) decide when Claude uses the skill at all. |
| `guidelines/` (planner) | **The part an organization edits**: who its readers are, its approved metric definitions, how pages are built (charts, filters, KPIs), and whether colors are suggested or pinned to the brand. |
| `references/` | Method and background, read only when a step needs it. |
| `assets/` | Ready-made files: the intake form, the confirmation card and the plan template. |
| `scripts/` | Small programs Claude runs: describe a data file, check a plan, build a page from a plan. |
| `evals/` | Test requests and test data. Not shipped. |

## The three technologies in the dashboard page

- **DuckDB** — a database engine. Normally it runs on a computer; here a version of it runs *inside the web browser* (that's "DuckDB-WASM": WebAssembly lets the browser run it). It does all the counting and adding up.
- **Mosaic** — a toolkit that links charts to DuckDB. When you click or drag on a chart, Mosaic asks DuckDB for fresh numbers and redraws every other chart, *while* you drag. Its charts are drawn with **Observable Plot**; anything Plot can't draw can be drawn with **D3** and still join in.
- **Cross-filtering** — the name for "click on one chart and all the others update". On the page, every chart writes its choice into its own little "selection", and one shared filter collects all of them. Each chart listens to everyone else's choices but not its own, so the chart you click stays fully visible with your choice highlighted.

Because DuckDB does the heavy lifting in the browser, the page can handle millions of rows and still respond instantly. There's no server to run besides a simple file server.

## How a page gets built

- **No template.** Each page is designed for its data and story: the charts, the layout and how numbers are shown are chosen fresh every time, so pages don't all look alike.
- **What's fixed:** the plan's content (titles, order, metrics, notes), how interaction behaves (one shared filter, live brushing, chips and Reset), the Style Profile and the colors.
- **The know-how** is in `references/mosaic-tech.md`: how to wire Mosaic, what Observable Plot can draw, and the mistakes already made once so they aren't made again.
- **Colors** are suggested for each dashboard (a calm grey base, one highlight color, one warning color), shown on the confirmation card so you can change them. An organization can pin its brand colors in `guidelines/dashboard.md` instead.

## See the working example

`examples/orders-dashboard/` has a plan and the page built from it. From the project folder:

```bash
python examples/orders-dashboard/make_data.py
```

```bash
python -m http.server 8000
```

Then open http://localhost:8000/examples/orders-dashboard/ in your browser. Try:
- clicking a category bar (everything else updates, and a chip appears above the KPIs)
- dragging across part of the year on the trend chart (the numbers change while you drag)
- picking a store in the menu
- clicking **Reset**

Why the extra "server" step: browsers refuse to let a page opened straight from your disk load data files, for security. `python -m http.server` is a tiny local web server that gets around that. Stop it with Ctrl+C.

## Where the dashboard can run

| Where | What's used | Notes |
|---|---|---|
| On your computer / your own website | Mosaic + DuckDB + Observable Plot in the page | Designed per dashboard |
| A claude.ai artifact | Simpler charts over pre-summarised data | DuckDB is too big to load inside an artifact, so the plan prepares the summary first |
