---
name: planning-dashboard
description: Plans interactive, cross-filtered dashboards from any tabular data before anything is built. Use this skill whenever someone asks for a dashboard, report page, KPI view, scorecard, monitoring page, or interactive charts, or asks to visualize, explore, track, summarize, or tell the story of a dataset (CSV, TSV, Parquet, JSON, Excel, or a database table), even if they never say the word "dashboard". Captures intent with a short intake form (goal, audience, cadence, success criteria), profiles the data with DuckDB, confirms its read with the person, and writes a validated plan that any dashboard executor can build from.
compatibility: Requires Python with the duckdb package for profiling, validation, and data export.
metadata:
  version: "0.2.1"
---

# Planning a dashboard

Good dashboards come from decisions made before any chart is drawn: what the page should help with, who reads it, how often, and what the numbers mean. This skill makes those decisions with the person and writes them down as a plan. Building the page is a separate job for an executor (another skill, Claude itself, or a program), so the plan must be complete enough to build without re-deciding anything.

Work from the person's own data and words. Don't assume a domain, column names, or metrics before profiling.

**Setup:** `pip install duckdb` if it isn't installed. Scripts are in `scripts/` relative to this skill's folder; run them, don't read them.

**Organization guidelines:** the files in `guidelines/` are where an organization customizes this skill. Always follow them over the defaults in `references/`.

## First turn: a rule, not a tip

Before any tool call, write the progress checklist from Workflow below into your reply; it pins you to step 1.

Then your first command is `python scripts/start_run.py out/<name> <data file> --skip <answered fields>`. **Nothing comes before it:** don't list the data folder, check the file's size, read its schema or metadata, or open another reference. The rule is in [guidelines/timing.md](guidelines/timing.md), which measures every run.

Why it is safe for any file: `start_run.py` handles size itself. Up to 20M rows it reads everything. Above that (a 91 GB, 6.1-billion-row Parquet file, say), it samples spread-out rows and takes the exact row count, nulls and ranges from the file's metadata. The quick look takes about 2 s and the background profile about 10 s, and `profile.txt` says what was sampled. A large or unfamiliar file is never a reason to inspect it yourself first. If the script fails, it says why; fix that and run it again.

What it does: creates the run folder, takes a quick look at the data, starts the full profile in the background, and prints the form; pass the form straight to the widget. Its "What's the ask?" offers 2–3 questions this data can answer, and its example text uses the data's own columns. (Exit code 2 means nothing is left to ask: skip the form.)

## Speed

The first dashboard must not wait on anything it doesn't need; see the budget in [guidelines/timing.md](guidelines/timing.md).
- **When answers arrive,** work in this order: `2-intake/intake.md`, then the explore rounds on the finished profile (step 1), then `design_seed.py` (step 3), then the brief (`2-intake/brief.md`, whose hook needs a computed number and whose concepts use the seed's provocations), then `3-layout/`.
- **Quick depth** has no card: it builds straight from the plan, whose Assumptions section records what was assumed. Every depth hands over the dashboard link as soon as the page exists.

## Workflow

Copy this checklist into your first reply, before any tool call, and tick it off as you go. Each step saves into its numbered folder in `out/<name>/`:

```
Dashboard plan progress:
- [ ] 1. Profile: start_run.py looks at the data first           → 1-profile/
- [ ] 2. Intake: show the form, save the answers, write the brief → 2-intake/
- [ ] 3. Layout and card: draft the page, confirm it once        → 3-layout/
- [ ] 4. Plan: export data, write and validate plan.md           → 4-dashboard/
- [ ] 5. Build the page from plan.md and share the link         → 5-handoff/
```

1. **Profile.** From the request, decide what's already answered (fields you're confident about go in `--skip`, per [references/intake.md](references/intake.md) sections 1 and 4), then run `start_run.py` (see Speed). It looks at the data first: a quick look at column types on a sample (saved as `1-profile/quick-look.json`), then the full profile in the background (`1-profile/profile.txt`). When the answers arrive, read that profile rather than profiling again; re-run `python scripts/profile.py <file> --columns a,b,c` only when the answers name columns to focus on. Then explore beyond the fixed profile: write your own questions about this data as SQL and run them with `python scripts/explore.py out/<name> <data file> <queries.sql>` (results land in `1-profile/explore.md`), for as many rounds as the answers raise new questions. Turn it all into observations and candidate metrics with [references/understand-data.md](references/understand-data.md), using approved definitions from [guidelines/metrics.md](guidelines/metrics.md) and glossary terms from the intake when the data has the columns they need.
2. **Intake.** Show the "Dashboard details" form `start_run.py` printed, built from the quick look: it asks only the missing questions, and "What's the ask?" offers 2–3 questions this data can answer (a picked one arrives as `Suggested ask: …`). Parse the answers per `intake.md` sections 2–4. Wording and signals come from [guidelines/goals.md](guidelines/goals.md). Then write the brief with [references/question-brief.md](references/question-brief.md): who reads it, what they ask, why, how they'll read it, and the hook; then 3–5 supporting questions, each with an angle (finding, comparison, visual, motion, honesty check). A `spec` request (it names its charts) skips the form, the supporting questions and the story.
3. **Layout and card.** Stack the page blocks for the goals from `guidelines/goals.md` at the cadence's density, built from the brief's angles (the hook is the primary surface), with finding-titles computed from the data. Run `python scripts/design_seed.py out/<name> --units <units>` for a fresh concept, chains of forms, palette, theme, icons and motion (it avoids what earlier runs used), and save it in `3-layout/`. Sketch five concepts for the hook first, one of them invented, using the seed's provocations (`question-brief.md` §3), so no list sets the limits. Then choose each chart's visual, with the seed's chains as starting points, [references/d3-toolkit.md](references/d3-toolkit.md) as the vocabulary, and [references/visual-language.md](references/visual-language.md) and [references/show-reel.md](references/show-reel.md) for the method: know the conventional form, draw something better, and keep every honesty rule, following [references/data-story.md](references/data-story.md) and [references/interaction.md](references/interaction.md). Derive the page's Style Profile from goal, audience and data character with [references/style-system.md](references/style-system.md), and suggest its colors (unless [guidelines/dashboard.md](guidelines/dashboard.md) pins brand colors). Then show the card from `intake.md` section 5 (`python scripts/confirmation_card.py card.json`): the data definitions, exclusions and suggested colors, each a row the person can change. Handle its follow-ups narrowly (section 6) until the person says "Looks right, build it". For quick, skip the card entirely and go on to the plan.
4. **Plan.** Pick the destination with [references/destinations.md](references/destinations.md) and export the data files it needs into `4-dashboard/` with DuckDB `COPY`. Write `4-dashboard/plan.md` next to them using [assets/plan-template.md](assets/plan-template.md); the format is [references/plan-format.md](references/plan-format.md). Run `python scripts/validate_plan.py plan.md` and fix what it reports until it passes. A broken plan only gets more expensive once it's built.
5. **Build.** Build the page yourself from `4-dashboard/plan.md` as one `index.html` in `4-dashboard/` next to its data, using the technology in [guidelines/dashboard.md](guidelines/dashboard.md) (Mosaic + DuckDB-WASM, with Observable Plot for static forms and D3 for unconventional and animated ones); how to wire it, and the pitfalls, are in [references/mosaic-tech.md](references/mosaic-tech.md). There is no template: design the page for this data and story, drawing each chart as its `~ draw:` line says (D3 for the forms Plot can't draw), with motion per [references/motion.md](references/motion.md) up to the Style Profile's `motion`, including morphs between views. With `surface: stage`, build the one-screen stage in [references/stage.md](references/stage.md): scenes from the brief, shared mark units, staged morphs, honest 3D. **Start from an empty file.** Don't open or copy pages from other runs, `examples/`, or anything built earlier in the conversation; the design seed decides the concept, forms and look, and the show-reel engine ([references/show-reel.md](references/show-reel.md)) morphs one set of marks through each chain. Type nothing into the code that the data can supply (categories, colors, dates, highlighted points). What's fixed is the plan's content (titles, story order, metrics, notes), its interaction rules ([references/interaction.md](references/interaction.md)), its Style Profile ([references/style-system.md](references/style-system.md)) and its colors. Give every mark a tooltip and every title, KPI and control help text ([references/interaction.md](references/interaction.md)). Serve the folder over http, try every interaction, run the honesty pass (`visual-language.md` Part 4) and, for a stage, the motion check (`show-reel.md` §7). Then critique it once, as a stranger would: is the hook obvious in five seconds, does any scene look like a stock dashboard, does every move feel continuous, would any single chart mislead as a screenshot? Fix the worst two findings and note them in the hand-off. Then make the shareable file: `python scripts/bundle_report.py out/<name>` writes `5-handoff/report.html` with the data embedded; it opens by double-click, with no server. As soon as the page exists, give the person its link and how to open it, then finish with `python scripts/run_folder.py summary out/<name>`. Changes the person asks for go back into the plan, which is re-validated and rebuilt.

## Run folder

Every run keeps a record of each step, so the person (or a reviewer) can see how the dashboard was decided. Pick a short name for `out/<name>`; `start_run.py` creates the folders, starts the clock, and saves `form.html`, `quick-look.json` and `profile.txt` itself. (Without a form, e.g. a spec request, create them with `python scripts/run_folder.py init out/<name>`.) Save the rest as you go:

| Folder | Save |
|---|---|
| `1-profile/` | `quick-look.json` and `profile.txt` (saved by `start_run.py`); `explore.sql` and `explore.md` (your own queries and their results, saved by `explore.py`); `observations.md` (the 3–5 sentences and candidate metrics) |
| `2-intake/` | `form.html` (saved by `start_run.py`); `intake.md`: each field with its value and where it came from (inferred from which words, answered on the form, or a picked ask); `brief.md`: reader, hook, supporting questions and their angles |
| `3-layout/` | `design-seed.json` (saved by `design_seed.py`); `layout.md`: blocks in order, each chart's finding-title, and the SQL and result behind every number in it; `card.json`, `card.html`, and `changes.md` listing each "Change assumption" or "Adjust" and what changed |
| `4-dashboard/` | `plan.md`, the exported data files, `validation.txt` (the validator's output), and the page once built |
| `5-handoff/` | `report.html` (the self-contained page to share, from `bundle_report.py`); `usage.json` (exact tokens, cost, model and skill version: `record_usage.py out/<name> --transcript <session>.jsonl` reads them from the Claude Code transcript; whoever has the transcript runs it, usually the person or the session that started the run, and `--tokens unknown` records model and version only); `handoff.md`: how the page was built (charts and libraries used), how to open it, the honesty pass (one line per chart), anything in the plan not built and why |

A skipped step stays empty (e.g. a quick request has no card, so `3-layout/` holds only `layout.md`). Finish with `python scripts/run_folder.py summary out/<name>`, which writes `README.md` with each step's status, files, and timing against `guidelines/timing.md`. Paths inside `plan.md` are relative to `4-dashboard/`.

Timing is read from when files were saved, so save in this order: `form.html` right before showing the form, `intake.md` as soon as the answers arrive, `card.html` right before showing the card, and `changes.md` (one line is enough) as soon as the card is answered. The time between those pairs is the person's, and doesn't count against any step.

## Asking rules

Questions cost the person time, so each one has to earn its place:
- Ask only when the answer changes the plan.
- After the intake form, don't open another round of questions: what the profile raises goes on the card as an assumption with its recommended value, and a Change gets ONE focused question.
- If the request, an attachment, or `guidelines/` already answers it, skip the question and state the assumption.
- If nobody answers, use the recommended options and list them under Assumptions in the plan.
- Never ask about chart library or styling; `guidelines/dashboard.md` and the Style Profile decide those. Colors are only suggested, as a row on the card.
- Never show internal ids or persona-style labels to the person; use the form's words from `guidelines/goals.md`.
