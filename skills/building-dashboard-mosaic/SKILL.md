---
name: building-dashboard-mosaic
description: Builds an interactive, cross-filtered dashboard web page with Mosaic and DuckDB-WASM from a dashboard plan (plan.md, plan format v1, as written by the planning-dashboard skill). Use this skill when a validated dashboard plan exists and the destination is a local or self-hosted HTML page, or when someone asks to build, rebuild, or preview a dashboard from a plan.md. Not for planning; if there is no plan yet, plan first.
compatibility: Requires Python for the build script and a web browser; the page loads Mosaic and DuckDB-WASM from a CDN at runtime.
---

# Building a dashboard with Mosaic

This skill is one executor for dashboard plans. The plan already records the decisions the person approved (who reads the page, what each number means, the story order), so build it exactly. Never re-decide a definition, title, or order. If something in the plan can't be built, stop and say what and why.

**Use it for** destinations `local` and `self-hosted`. For `artifact` or `dashboard-type`, the page can't run DuckDB; build by hand from the plan's pre-aggregated data instead.

## Workflow

Copy this checklist into your response and tick it off as you go:

```
Build progress:
- [ ] 1. Generate the page
- [ ] 2. Serve and open it
- [ ] 3. Review against the plan
- [ ] 4. Deliver
```

1. **Generate the page.** Run `python scripts/build_page.py <path/to/plan.md>`. It reads the plan, fills the CONFIG block of [assets/mosaic-dashboard.html](assets/mosaic-dashboard.html), and writes `index.html` next to the plan. If it reports plan errors, send the plan back to the planner (or fix the plan with the person); don't hand-edit around them.
2. **Serve and open it.** Browsers block data loading from `file://`, so in the plan's folder run `python -m http.server 8000` and open `http://localhost:8000/`. Check the browser console has no errors.
3. **Review.** Follow [references/review.md](references/review.md): check the totals, click one bar, drag one brush, test Reset, and check phone width.
4. **Deliver.** Tell the person how to open it (the serve command and URL), list anything in the plan not built and why, and offer the planner's refine step.

## When the template isn't enough

The template covers the forms in plan format v1 (`trend`, `bar`, `histogram`, `scatter`), KPIs, menus, a detail table, per-chart SQL, and style tokens. For anything else, extend the engine following [references/mosaic.md](references/mosaic.md). Keep the CONFIG vocabulary unchanged so `build_page.py` keeps working.
