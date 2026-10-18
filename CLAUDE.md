# Mosaic Dashboard Skill

Two Claude skills:
- `skills/planning-dashboard/`: the planner. Goal-based intake (references/intake.md), DuckDB profiling, confirmation card, a validated `plan.md` plus exported data. For now it also builds the page itself, designed fresh each time from a design seed (`scripts/design_seed.py`) with Mosaic + DuckDB-WASM, D3 show-reel morphs, d3-3d and Observable Plot, per `references/show-reel.md`, `references/stage.md` and `references/mosaic-tech.md`; there is deliberately no page template, and no page reuses another's code.
- `skills/building-dashboard-mosaic/`: a parked executor (not used for now). It turns a plan into a page with `scripts/build_page.py`.

The plan format (`skills/planning-dashboard/references/plan-format.md`, v2) is the contract between them. Executors are swappable; organizations customize the planner through `guidelines/` only.

## Rules for editing
- Follow the Agent Skills spec and Anthropic's authoring best practices: `name` = folder name; third-person description that says what and when; SKILL.md under 500 lines; every file linked one level deep from SKILL.md; forward slashes in paths.
- Frontmatter keys only from: name, description, license, compatibility, metadata, allowed-tools (claude.ai rejects anything else).
- Stay domain-agnostic: no dataset, column names, or metrics in either skill except under `evals/`.
- Org-specific choices belong in `guidelines/`; method in `references/`. Don't mix them.
- Plan format changes: update `plan-format.md`, `plan_format.py`, `validate_plan.py`, `assets/plan-template.md`, and the executor together. Then run `python tools/sync_plan_format.py`, and bump `plan_version` if the change breaks old plans.
- Changes to `references/mosaic-tech.md`: test any snippet or pitfall in a browser first (served over http). `examples/orders-dashboard/index.html` is one hand-built page using it: brushing updates the other charts and numbers while dragging, click, menu, Reset and chips work, no console errors. It's an example, not a template; don't turn it into one.
- Scripts handle their own errors with specific messages; explain any constant.
- Keep `examples/orders-dashboard/plan.md` valid; it's the end-to-end smoke test.

## Interactive testing
A separate "user" session runs in `C:/Users/kasiv/projects/mosaic-dashboard-playground`, which links to these skills. Feedback from it arrives as messages: fix the skill here, not in the playground.
