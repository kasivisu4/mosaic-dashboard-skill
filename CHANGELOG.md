# Changelog

The planning-dashboard skill's version is in `skills/planning-dashboard/SKILL.md` (`metadata.version`); each release is a git tag (`v0.2.0`). Every run records the version that built it in `5-handoff/usage.json`, so dashboards can be compared across versions (`git diff v0.1.0 v0.2.0 -- skills/`).

## 0.2.0 (2026-10-18)

Out-of-the-box, animated, honest dashboards, designed fresh every run.

- **Design:** `scripts/design_seed.py` draws a fresh layout concept, chains of chart forms, palette, theme, icons, motion and two creative provocations per run, avoiding earlier runs' choices. Five concepts for the hook (one invented) before any visual is chosen (`references/question-brief.md`).
- **Visual method:** `references/visual-language.md` (the conventional playbook, what to draw instead, 19 honesty rules), `references/d3-toolkit.md` (D3 vocabulary, one sentence each), `references/show-reel.md` (polygon morph engine: one set of marks through many forms, 2D to 3D with d3-3d; smoothness rules; motion check), `references/stage.md` (one-screen story pages), `references/motion.md` (Motion switch, glide Play, morphs).
- **Intake:** new "How should the page tell the story?" question (one-page story, dashboard grid, scrolling report) setting the plan's `surface`; new `impact` goal.
- **Data:** `scripts/explore.py` runs the model's own exploratory SQL and saves it with results; from-to titles use full periods only.
- **Plan format (v2, compatible):** `ratio(num,den)` values, `~ draw:` lines, `surface: stage`, `destination: file`.
- **Sharing:** `scripts/bundle_report.py` writes one self-contained `report.html` with the data embedded; opens by double-click, no server. `tools/build_gallery.py` publishes runs to `docs/gallery/` for GitHub Pages.
- **Every page:** tooltips on every mark, help text on every title, KPI and control; a critique pass before sharing.
- **Cost tracking:** `scripts/record_usage.py` records model, tokens, estimated cost and skill version per run.

## 0.1.0

The planner before this release: goal-based intake, DuckDB profiling, confirmation card, validated `plan.md`, pages built with Mosaic + DuckDB-WASM + Observable Plot (commit 5f72e1a).
