# How the skill works (plain-language guide)

This is for you, not for Claude. It isn't shipped with the skill.

## The big picture

There are two skills, and they do separate jobs:

1. **The planner** (`planning-dashboard`) figures out *who* will read the dashboard, *what* the data contains and means, and *what story* it should tell. It asks a few short questions where they matter, then writes everything down as a **plan** (`plan.md`) and checks the plan with a script.
2. **An executor** turns the plan into a dashboard. `building-dashboard-mosaic` is one executor. Others can be added (a different charting tool, a company's BI system, or a person), because they only need the plan.

The plan is the handshake between the two. Its format is written down (`references/plan-format.md`), so anyone can build an executor without touching the planner.

## What each folder is for

| Folder / file | Plain meaning |
|---|---|
| `SKILL.md` | The "front page" Claude reads first. Its top lines (name + description) decide when Claude uses the skill at all. |
| `guidelines/` (planner) | **The part an organization edits**: who its readers are, its approved metric definitions, its colors. |
| `references/` | Method and background, read only when a step needs it. |
| `assets/` | Ready-made files: the plan template (planner) and the dashboard page template (executor). |
| `scripts/` | Small programs Claude runs: describe a data file, check a plan, build a page from a plan. |
| `evals/` | Test requests and test data. Not shipped. |

## The three technologies in the dashboard page

- **DuckDB** — a database engine. Normally it runs on a computer; here a version of it runs *inside the web browser* (that's "DuckDB-WASM": WebAssembly lets the browser run it). It does all the counting and adding up.
- **Mosaic** — a charting toolkit built to work with DuckDB. When you click or drag on a chart, Mosaic asks DuckDB for fresh numbers and redraws every other chart.
- **Cross-filtering** — the name for "click on one chart and all the others update". In the template, every chart writes its choice into its own little "selection", and one shared filter collects all of them. Each chart listens to everyone else's choices but not its own, so the chart you click stays fully visible with your choice highlighted.

Because DuckDB does the heavy lifting in the browser, the page can handle millions of rows and still respond instantly. There's no server to run besides a simple file server.

## How the Mosaic executor builds a page

`assets/mosaic-dashboard.html` is one file with two parts:

- A **CONFIG block** at the top: the plan's settings (title, KPIs, charts, filters, colors).
- The **engine** below it: loads DuckDB, draws the charts, wires up filtering. It's tested once and reused every time.

`scripts/build_page.py` reads `plan.md` and writes the CONFIG block for you, so no one hand-edits code to make a dashboard. If the plan is broken, it refuses and lists what's wrong.

## See the working example

`examples/orders-dashboard/` has a plan and the page built from it. From the project folder:

```bash
python examples/orders-dashboard/make_data.py
```

```bash
python skills/building-dashboard-mosaic/scripts/build_page.py examples/orders-dashboard/plan.md
```

```bash
python -m http.server 8000
```

Then open http://localhost:8000/examples/orders-dashboard/ in your browser. Try:
- clicking a store bar (everything updates, and a chip appears under the title)
- dragging across part of the year on the trend chart
- clicking **Reset**

Why the extra "server" step: browsers refuse to let a page opened straight from your disk load data files, for security. `python -m http.server` is a tiny local web server that gets around that. Stop it with Ctrl+C.

## Where the dashboard can run

| Where | What's used | Notes |
|---|---|---|
| On your computer / your own website | Mosaic + DuckDB in the page | The template above |
| A claude.ai artifact | Simpler charts over pre-summarised data | DuckDB is too big to load inside an artifact, so the plan prepares the summary first |
