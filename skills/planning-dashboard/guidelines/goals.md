# Goals, audiences and cadence

> **Customize this file** to match how your organization talks about dashboards: the wording on the intake form, the words that signal each goal, and the page blocks each goal produces. Keep the ids (`answer`, `spec`, …) unchanged: plans and validators use them. `scripts/intake_form.py` and `scripts/confirmation_card.py` read the labels and icons from the tables below, so keep their column layout; table order is the order shown on the form.

## Goals

The person picks one or two; the first one sets the top of the page.

| id | Form card (title, subtitle, icon) | Signals in a request |
|---|---|---|
| `answer` | Answer a question · "Why did X change?" · `ti-help-circle` | why, what changed, which, what's driving, root cause |
| `spec` | I know what I want · "I'll describe the charts" · `ti-list-details` | names specific charts, columns, or filters |
| `explore` | Explore my data · "Show me what's interesting" · `ti-compass` | data with no question, what's interesting, dig into, slice |
| `monitor` | Keep an eye on it · "Spot issues early" · `ti-activity` | track, daily, keep an eye on, alert, are we on target |
| `present` | Make a case · "Tell a clear story" · `ti-presentation` | for leadership, board, client, show X how, presentation, story |

## Page blocks per goal

Used for the layout preview on the confirmation card and for the plan's Story. Stack one block per goal, in goal order, except `monitor` (always on top) and `present` (always at the bottom).

| Goal | Block | Plan lines |
|---|---|---|
| `monitor` | status row: on/off track vs target, exceptions, last-updated stamp | `KPIs` with `target>=`/`target<=`, an `exceptions` line, `Last updated` |
| `answer` | headline banner, 3 KPI cards, driver chart + trend chart | takeaway paragraph, `KPIs` (3), a ranked `bar` of drivers, a `trend` |
| `explore` | filter bar, dense grid of distributions, detail table | `Menus`, several `histogram`/`bar`/`scatter`, `Detail table: yes` |
| `present` | annotated story section | charts with `> narrative` and `@ annotation` lines |
| `spec` | exactly the charts asked for, nothing else | one line per requested chart |

## Audiences

| id | Form label | Signals | Rules |
|---|---|---|---|
| `me` | Just me | for me, my own, quick look | SQL on page allowed |
| `team` | My team | for the team, my squad, ops | SQL on page allowed |
| `leadership` | Leadership | VP, exec, leadership, board | at most 4 KPIs, no SQL on page, plain-word labels |
| `clients` | Clients or regulators | client, customer-facing, regulator, auditor | at most 4 KPIs, no SQL on page, every number reconciled (turns `reconcile` on) |

## Cadence

| id | Form label | Density | Emphasis |
|---|---|---|---|
| `one-time` | One-time deep dive | rich | full investigation: drivers, distributions, narrative, detail tables |
| `weekly` | Weekly review | medium | week-over-week change, short trend, top movers |
| `monthly` | Monthly report | medium to rich | period comparisons, drivers, short narrative annotations |
| `daily` | Daily check | sparse, glanceable (at most 4 charts) | status vs target, exceptions list, last-updated stamp; few or no dense tables |

When cadence and goal pull in different directions (daily + explore), keep the goal's blocks and apply the cadence's density.

## Review depth

| id | Form label |
|---|---|
| `quick` | Just build it |
| `guided` | Check assumptions first |
| `deep` | Full review with SQL |

## Glossary prompt

Show the glossary question on the intake form when the request or data uses business terms that don't match column names, or when the domain is regulated: lending, banking, insurance, healthcare. Add your own domains here.
