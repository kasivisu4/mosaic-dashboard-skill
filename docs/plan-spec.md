# Plan spec (for executor authors)

The dashboard plan is the contract between the planner and any executor. The full definition lives with the planner, so it ships with it:

**→ [skills/planning-dashboard/references/plan-format.md](../skills/planning-dashboard/references/plan-format.md)** (plan format v1)

## What an executor can rely on
- `plan.md` passed `validate_plan.py`: every section is present, every column the plan names exists in its data file, the row counts in the header are right, and the export SQL runs.
- Data files sit next to `plan.md`. The first file in the header is the default for every KPI, chart, and menu.
- Titles are approved findings: render them verbatim.
- Interaction rules are fixed (see `references/interaction.md`): one shared crossfilter, brush on `trend`/`histogram`/`scatter`, click on `bar`, Reset, readable active filters, and KPIs showing filtered plus total.
- `## Style` holds the organization's tokens; apply them.

## What an executor must do
- Build every Story line in order, or report which ones it can't and why. Never substitute silently.
- Put the plan text in a build note on the page.
- Refuse plans that don't parse, and point back to the planner.

## Parsing
Python executors can import `skills/planning-dashboard/scripts/plan_format.py` (`parse(text) -> (plan, errors)`), or copy it as `building-dashboard-mosaic` does (keep copies in sync with `tools/sync_plan_format.py`).

## Versioning
`plan_version` in the header. Breaking changes bump it; executors should refuse versions they don't know.
