---
plan_version: 2
goals: {one or two of answer, spec, explore, monitor, present, in page order}
audience: {one or more of me, team, leadership, clients}
cadence: {one-time | daily | weekly | monthly}
review_depth: {quick | guided | deep}
success_criteria: "{what makes it useful, in the person's words, or none stated}"
reconcile: {true | false}
comparison_period: {date column:day | week | month | quarter | year, or delete this line}
destination: {local | artifact | dashboard-type | self-hosted}
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
2. "{finding stated as a title}" | {trend | bar | histogram | scatter | exceptions} | {key=value ...} | {brush | click | none}
   {> narrative under the chart, optional}
   {@ date, category or number: annotation label, optional}

## Interaction
- Menus: {columns, or none}
- Detail table: {yes | no}
- SQL on page: {yes | no}
- Last updated: {date column, or none}

## Style
- accent: {#hex from guidelines/style.md}
- alert: {#hex}
- currency: {ISO code}

## Data for the executor
```sql
{the COPY statement that produced each data file}
```
