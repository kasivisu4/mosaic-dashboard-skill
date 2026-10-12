# Plan format (version 2)

The plan is the contract between the planner and any executor (Claude, another LLM, or a program). It is Markdown a person can read and edit, with a small YAML header and a few strict line formats a program can parse. `scripts/validate_plan.py` enforces everything below.

## Contents
- File layout
- Header
- Sections
- Story lines
- Value expressions
- Changes from version 1
- Example

## File layout

```
plan.md                  the plan
<exported data files>    listed in the header, next to the plan
```

Every path in the plan (`source`, `data` files, paths inside SQL) is relative to the plan's folder, not the project root, because the validator and executors run from there.

## Header

```yaml
---
plan_version: 2
goals: monitor, answer         # 1–2 of answer | spec | explore | monitor | present, in page order
audience: team                 # one or more of me | team | leadership | clients | regulators
cadence: weekly                # one-time | daily | weekly | monthly
review_depth: guided           # quick | guided | deep
success_criteria: "store return rates readable at a glance"   # or "none stated"
reconcile: false               # true when numbers must match an official source
comparison_period: order_date:week   # optional: <date column>:<day | week | month | quarter | year>
destination: local             # local | artifact | dashboard-type | self-hosted
source: ../data/orders.csv     # the original data, relative to the plan's folder
data:                          # files the executor reads; first one is the default
  - file: orders_clean.parquet
    rows: 7997
---
```

- `goals` and `audience` may be written `a, b` or as a YAML list.
- `comparison_period`: KPI tiles show the latest period to date and the change from the same span of the period before (e.g. Mon–Wed this week vs Mon–Wed last week), so a partial last period is never compared with a full one.

## Sections

In this order, after the header:

| Section | Content |
|---|---|
| `# <Title>` | Page title. The paragraph after it (optional) is the takeaway: the headline answer when `answer` is a goal. |
| `## Assumptions` | Bullets, each `- <name>: <what was assumed>` so it can be changed by name. Required when `review_depth: quick`; otherwise `- none`. |
| `## Data` | Bullets: `1 row = …`, `Excluded: …` (or `none`), one line per metric or glossary definition, marked `(confirmed)` or `(assumed)`, and, when `reconcile: true`, `Reconcile with: <source> (matched | not yet checked)`. |
| `## Story` | Numbered story lines (below), in page order. |
| `## Interaction` | `- Menus: col, col` (or `none`), `- Detail table: yes/no`, `- SQL on page: yes/no`, optional `- Last updated: <date column>` (the page shows the latest date in it). |
| `## Style` | The Style Profile, one `- field: value` per line (fields and values in `style-system.md`; all of them or none), plus the tokens `- accent: #hex`, `- alert: #hex`, `- currency: ISO code` (optional). |
| `## Data for the executor` | One ```` ```sql ```` block per data file: the exact statement that produced it. |

## Story lines

```
1. KPIs: <Label> = <value> [<format>]; <Label> = <value> [<format>] target<=<number>
2. "<finding-title>" | <form> | <key=value ...> | <interaction>
   > optional narrative shown under the chart
   @ <where>: <annotation label>
```

KPIs: `target>=N` or `target<=N` (optional) sets the on/off-track status. N is in the value's own units; rates may be written as `8%` or `0.08`.

| form | keys | interaction |
|---|---|---|
| `trend` | `x=<date column>:<day/week/month/quarter/year>` `y=<value>` | `brush` or `none` |
| `bar` | `category=<column>` `value=<value>` | `click` or `none` |
| `histogram` | `value=<numeric column>` | `brush` or `none` |
| `scatter` | `x=<numeric column>` `y=<numeric column>` | `brush` or `none` |
| `exceptions` | `category=<column>` `value=<value>` and `above=<number>` or `below=<number>` | `none` |

- `exceptions` lists the categories whose value breaks the limit, worst first, under the page filter (e.g. stores whose return rate is above 10%).
- Any line may add `from=<file>` to read a data file other than the first, and `format=<format>` for how values are shown.
- `format`: `number`, `compact`, `percent`, `currency`.
- Annotations (`@ …`, any number) mark a moment on the chart: a date for `trend` (`@ 2025-03-01: Price change`), a category value for `bar` (`@ East: Highest returns`), a number for `histogram` and `scatter` (an x position).

## Value expressions

`count()`, `sum(col)`, `avg(col)`, `median(col)`, `min(col)`, `max(col)`, `rate(col)` (share of rows where a boolean or 0/1 column is true). Every column must exist in the data file the line reads.

## Changes from version 1

v1 had `persona` and `mode`. v2 replaces them with the intake fields `goals`, `audience`, `cadence`, `review_depth` (was `mode`), `success_criteria` and `reconcile`, and adds `comparison_period`, KPI targets, the `exceptions` form, annotations, and `Last updated`. Executors refuse v1 plans; re-run the planner to upgrade one.

## Example

````markdown
---
plan_version: 2
goals: monitor, answer
audience: team
cadence: weekly
review_depth: quick
success_criteria: "a store with too many returns stands out at a glance"
reconcile: false
comparison_period: order_date:week
destination: local
source: orders.parquet
data:
  - file: orders_clean.parquet
    rows: 8000
---

# Store sales, 2025

Revenue was steady all year; returns run at about 9% of orders in every store.

## Assumptions
- Revenue: sum of revenue, returns included
- Return-rate target: at most 9% of orders

## Data
- 1 row = one order · 8,000 rows · Jan–Dec 2025
- Excluded: none
- Return rate = returned orders / all orders (assumed)

## Story
1. KPIs: Revenue = sum(revenue) [currency]; Orders = count() [compact]; Return rate = rate(returned) [percent] target<=9%
2. "East is the only store above a 9% return rate" | exceptions | category=store value=rate(returned) above=9% format=percent | none
3. "Weekly revenue held steady through the year" | trend | x=order_date:week y=sum(revenue) | brush
   @ 2025-12-29: Partial week
4. "Shoes lead revenue in every store" | bar | category=category value=sum(revenue) | click

## Interaction
- Menus: store
- Detail table: no
- SQL on page: no
- Last updated: order_date

## Style
- register: operational
- density: balanced
- surface: status
- focus: stores above the return-rate target
- color_mode: status
- direction: down-good
- type_scale: standard
- interaction: light
- motion: transitions
- chart_set: KPIs, exceptions, trend, bar
- anomalies: spotlight
- narrative: captions
- provenance: footnote
- numbers: precise
- data_character: time-heavy, categorical, flag-driven
- currency: USD

## Data for the executor
```sql
COPY (SELECT * FROM 'orders.parquet') TO 'orders_clean.parquet'
```
````
