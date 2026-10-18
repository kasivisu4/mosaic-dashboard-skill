# Interaction

The plan states interaction as rules; every executor implements them the same way. `references/mosaic-tech.md` shows how to do each with Mosaic's own selections and interactors:

- One shared filter for the whole page. Every chart and KPI responds to it.
- A chart is never filtered by its own selection (crossfilter), but it highlights what's selected in it.
- `trend`, `histogram`, `scatter` filter by **brush** (drag a range). `bar` filters by **click** (shift-click adds).
- There's always a visible **Reset** and a readable list of active filters.
- The detail table (if any) follows the filters. KPIs show the filtered value and the unfiltered total.

**Tooltips and help.** It's an HTML page, so everything the reader can point at explains itself:
- **Every mark has a tooltip** on hover and on keyboard focus (tap on touch): its labels, the exact value with units, the share or rank where the chart implies one, the period (marked partial when it is), and the filters it reflects. It follows the pointer, never covers the mark, and uses the page's number formats. This is part of honesty: the tooltip gives the precise value behind every visual approximation (a color, a 3D height, a slice).
- **Every chart title, KPI, control, legend and axis has help text**: a small info icon (`ti-info-circle`) with a one-or-two-sentence definition on hover or focus: what the number is, its denominator, which filters apply, and any caveat (for example "streaming calls only"). Write it from the plan's `## Data` definitions, in the audience's words.
- Controls also say what they do ("Click a family to filter every chart; shift-click adds another") when the reader hovers them.

Per goal and audience (see `guidelines/goals.md`):
- **monitor:** at most one brush and one click; the status row and exceptions follow the filters.
- **answer:** the driver bar filters by click; the trend by brush.
- **explore:** menus on every useful dimension, detail table on, every chart interactive.
- **present:** one interaction per section at most.
- **impact:** a few rewarding interactions over many controls: Play through time, click to focus, rich hover; every animated chart still follows the page filter.
- **leadership, clients or regulators** in the audience: no SQL on the page. The Style Profile's `interaction` level (references/style-system.md) sets how many controls the page gets.
