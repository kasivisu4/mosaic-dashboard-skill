# Interaction

The plan states interaction as rules; every executor implements them the same way. `assets/dashboard-kit.js` implements all of them with Mosaic's own selections and interactors:

- One shared filter for the whole page. Every chart and KPI responds to it.
- A chart is never filtered by its own selection (crossfilter), but it highlights what's selected in it.
- `trend`, `histogram`, `scatter` filter by **brush** (drag a range). `bar` filters by **click** (shift-click adds).
- There's always a visible **Reset** and a readable list of active filters.
- The detail table (if any) follows the filters. KPIs show the filtered value and the unfiltered total.

Per goal and audience (see `guidelines/goals.md`):
- **monitor:** at most one brush and one click; the status row and exceptions follow the filters.
- **answer:** the driver bar filters by click; the trend by brush.
- **explore:** menus on every useful dimension, detail table on, every chart interactive.
- **present:** one interaction per section at most.
- **leadership, clients or regulators** in the audience: no SQL on the page. The Style Profile's `interaction` level (references/style-system.md) sets how many controls the page gets.
