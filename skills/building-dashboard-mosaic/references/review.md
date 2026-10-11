# Review

A page that looks right can still be wrong: a chart that ignores the filter, a total that drifted from the data, an analyst page without SQL. Check these before the person sees it, and fix only what doesn't change a plan decision.

## Checklist
Record pass or fail with evidence for each:

- [ ] Page loads with no browser console errors.
- [ ] Unfiltered KPI values match DuckDB run on the data file, e.g. `python -c "import duckdb; print(duckdb.sql(\"SELECT sum(revenue) FROM 'file.parquet'\"))"`.
- [ ] Titles match the plan and are true for the data shown. If a title's claim is false, stop and report it; don't rewrite it.
- [ ] Clicking a bar filters every other chart and the KPIs, highlights the clicked bar, and adds a filter chip.
- [ ] Dragging a brush on a trend or histogram does the same.
- [ ] Reset clears all filters and chips.
- [ ] SQL is shown only if the plan says `SQL on page: yes`.
- [ ] Readable at phone width (about 375px) with no sideways scrolling, and in dark mode.

## Fixing
- Wiring, layout, or formatting problems: fix the engine or template, rebuild with `build_page.py`, and re-check.
- Problems that need a plan change (wrong column, false title, missing metric): report them for the planner's refine step.

The build note at the bottom of the page already contains the full plan; `build_page.py` adds it.
