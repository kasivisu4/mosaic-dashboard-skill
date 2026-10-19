---
plan_version: 2
goals: {one or two of answer, spec, explore, monitor, present, impact, in page order}
audience: {one or more of me, team, leadership, clients, regulators}
cadence: {one-time | daily | weekly | monthly}
review_depth: {quick | guided | deep}
success_criteria: "{what makes it useful, in the person's words, or none stated}"
reconcile: {true | false}
comparison_period: {date column:day | week | month | quarter | year, or delete this line}
destination: {file | local | artifact | dashboard-type | self-hosted}
source: {path to the original data, relative to this plan's folder}
data:
  - file: {exported file}
    rows: {row count}
---

# {Dashboard title}

{One or two sentence takeaway (the headline answer for an answer goal), or delete this line}

## Assumptions
- {name}: {what was assumed without asking, or "none"}

## Data
- 1 row = {grain} · {row count} rows · {time span, if any}
- Excluded: {rows or values, and why, or "none"}
- {Metric or term} = {definition, with denominator for rates} ({confirmed | assumed})
- Reconcile with: {source and figure} ({matched | not yet checked}) {only when reconcile: true, else delete}

## Story
1. KPIs: {Label} = {value} [{format}]; {Label} = {value} [{format}] {target>=N or target<=N, optional}
2. "{finding stated as a title}" | {trend | bar | histogram | scatter | map | exceptions} | {key=value ...} | {brush | click | none}
   {> narrative under the chart, optional}
   {~ draw: visual instead of conventional form, why (optional)}
   {@ date, category or number: annotation label, optional}

## Interaction
- Menus: {columns, or none}
- Detail table: {yes | no}
- SQL on page: {yes | no}
- Last updated: {date column, or none}

## Style
- register: {analytic | operational | editorial | formal | evidentiary}
- density: {sparse | balanced | dense}
- surface: {headline | status | grid | narrative | ledger | exact | stage}
- focus: {what the focus color marks, one phrase}
- color_mode: {focus | status | categorical | sequential | diverging}
- direction: {up-good | down-good | none}
- type_scale: {compact | standard | display}
- interaction: {none | light | full}
- motion: {none | transitions | reveal}
- chart_set: {forms the page may use, e.g. KPIs, bar, trend}
- anomalies: {ignore | flag | spotlight | explain | footnote}
- narrative: {none | captions | annotated | story}
- provenance: {hidden | footnote | inline | per-number}
- numbers: {rounded | precise | exact}
- data_character: {traits from style-system.md, comma-separated}
- accent: {#hex: the suggested focus color, or the brand color pinned in guidelines/dashboard.md}
- alert: {#hex: the suggested breach color}
- currency: {ISO code}

## Data for the executor
```sql
{the COPY statement that produced each data file}
```
