---
name: planning-dashboard
description: Plans interactive, cross-filtered dashboards from any tabular data before anything is built. Use this skill whenever someone asks for a dashboard, report page, KPI view, scorecard, monitoring page, or interactive charts, or asks to visualize, explore, track, summarize, or tell the story of a dataset (CSV, TSV, Parquet, JSON, Excel, or a database table), even if they never say the word "dashboard". Captures intent with a short intake form (goal, audience, cadence, success criteria), profiles the data with DuckDB, confirms its read with the person, and writes a validated plan that any dashboard executor can build from.
compatibility: Requires Python with the duckdb package for profiling, validation, and data export.
---

# Planning a dashboard

Good dashboards come from decisions made before any chart is drawn: what the page should help with, who reads it, how often, and what the numbers mean. This skill makes those decisions with the person and writes them down as a plan. Building the page is a separate job for an executor (another skill, Claude itself, or a program), so the plan must be complete enough to build without re-deciding anything.

Work from the person's own data and words. Don't assume a domain, column names, or metrics before profiling.

**Setup:** `pip install duckdb` if it isn't installed. Scripts are in `scripts/` relative to this skill's folder; run them, don't read them.

**Organization guidelines:** the files in `guidelines/` are where an organization customizes this skill. Always follow them over the defaults in `references/`.

## Speed

The first dashboard must not wait on anything it doesn't need. Every run is measured against the budget in [guidelines/timing.md](guidelines/timing.md). In particular:
- **First turn is one command:** `python scripts/start_run.py out/<name> <data file> --skip <answered fields>` creates the run folder, takes a quick look at the data (well under a second), starts the full profile in the background, and prints the form; pass it straight to the widget. Its "What's the ask?" offers 2–3 questions this data can answer, and its example text uses the data's own columns. Read no other reference before the form. (Exit code 2 means nothing is left to ask: skip the form.)
- **When answers arrive,** write `2-intake/intake.md` first, then continue from the profile that's already done.
- **Quick depth** builds without a card first. Every depth hands over the dashboard link before the browser review.

## Workflow

Copy this checklist into your response and tick it off as you go. Each step saves into its numbered folder in `out/<name>/`:

```
Dashboard plan progress:
- [ ] 1. Profile: start_run.py looks at the data first           → 1-profile/
- [ ] 2. Intake: show the form built from it, save the answers   → 2-intake/
- [ ] 3. Data check (asked in guided and deep)                   → 3-data-check/
- [ ] 4. Layout and story, every number in a title computed      → 4-layout/
- [ ] 5. Confirmation card (quick: after building)               → 5-confirm/
- [ ] 6. Export data, write and validate the plan                → 6-dashboard/
- [ ] 7. Hand off, then share the dashboard link                 → 7-handoff/
- [ ] 8. Review, success criteria, next steps, run summary       → 8-review/, README.md
```

1. **Profile.** From the request, decide what's already answered (fields you're confident about go in `--skip`, per [references/intake.md](references/intake.md) sections 1 and 4), then run `start_run.py` (see Speed). It looks at the data first: a quick look at column types on a sample (saved as `1-profile/quick-look.json`), then the full profile in the background (`1-profile/profile.txt`). When the answers arrive, read that profile rather than profiling again; re-run `python scripts/profile.py <file> --columns a,b,c` only when the answers name columns to focus on. Turn it into observations and candidate metrics with [references/understand-data.md](references/understand-data.md), using approved definitions from [guidelines/metrics.md](guidelines/metrics.md) and glossary terms from the intake when the data has the columns they need.
2. **Intake.** Show the "Dashboard details" form `start_run.py` printed, built from the quick look: it asks only the missing questions, and "What's the ask?" offers 2–3 questions this data can answer (a picked one arrives as `Suggested ask: …`). Parse the answers per `intake.md` sections 2–4. Wording and signals come from [guidelines/goals.md](guidelines/goals.md). A `spec` request (it names its charts) skips the form and the story.
3. **Data check.** Confirm the grain, metric definitions, glossary terms, and exclusions the profile surfaced (per review depth, in `intake.md` section 4).
4. **Draft the layout and story.** Stack the page blocks for the goals from `guidelines/goals.md` at the cadence's density, with finding-titles computed from the data, following [references/data-story.md](references/data-story.md), [references/interaction.md](references/interaction.md), and the chart rules in [guidelines/style.md](guidelines/style.md).
5. **Confirmation card.** For guided and deep, show the card from `intake.md` section 5, generated by `python scripts/confirmation_card.py card.json`, and handle its follow-ups narrowly (section 6) until the person says "Looks right, build it". For quick, go on and show the same card after building, as "here's what I assumed".
6. **Export data, write and validate the plan.** Pick the destination with [references/destinations.md](references/destinations.md) and export the data files it needs into `6-dashboard/` with DuckDB `COPY`. Write `6-dashboard/plan.md` next to them using [assets/plan-template.md](assets/plan-template.md); the format is [references/plan-format.md](references/plan-format.md). Run `python scripts/validate_plan.py plan.md` and fix what it reports until it passes. A broken plan only gets more expensive once it's built.
7. **Hand off.** If a dashboard executor skill is available (for example `building-dashboard-mosaic`), use it with the plan. Otherwise, if the person names a tool or service, give them `plan.md` and the data files. With neither, build the page yourself, following the plan exactly. As soon as the page exists, give the person its link and how to open it; don't hold it back for the review.
8. **Review, success criteria, and refine.** Record the review checks, say in one line whether the result meets the success criteria (`intake.md` section 7), then offer 2–3 specific next steps drawn from this data. Finish with `python scripts/run_folder.py summary out/<name>`. Changes go back into the plan, which is re-validated and handed off again.

## Run folder

Every run keeps a record of each step, so the person (or a reviewer) can see how the dashboard was decided. Pick a short name for `out/<name>`; `start_run.py` creates the folders, starts the clock, and saves `form.html`, `quick-look.json` and `profile.txt` itself. (Without a form, e.g. a spec request, create them with `python scripts/run_folder.py init out/<name>`.) Save the rest as you go:

| Folder | Save |
|---|---|
| `1-profile/` | `quick-look.json` and `profile.txt` (saved by `start_run.py`); `observations.md` (the 3–5 sentences and candidate metrics) |
| `2-intake/` | `form.html` (saved by `start_run.py`); `intake.md`: each field with its value and where it came from (inferred from which words, answered on the form, or a picked ask) |
| `3-data-check/` | `data-check.md`: each question asked, the options, the answer, and the resulting definition or exclusion |
| `4-layout/` | `layout.md`: blocks in order, each chart's finding-title, and the SQL and result behind every number in it |
| `5-confirm/` | `card.json`, `card.html`, and `changes.md` listing each "Change assumption" or "Adjust" and what changed |
| `6-dashboard/` | `plan.md`, the exported data files, `validation.txt` (the validator's output), and the page once built |
| `7-handoff/` | `handoff.md`: which executor, the exact command, how to open the page, anything not built |
| `8-review/` | `review.md`: checks run on the page, the success-criteria verdict, and the suggested next steps |

A skipped step stays empty (e.g. a quick spec request has no `5-confirm/` before building). Finish with `python scripts/run_folder.py summary out/<name>`, which writes `README.md` with each step's status, files, and timing against `guidelines/timing.md`. Paths inside `plan.md` are relative to `6-dashboard/`.

Timing is read from when files were saved, so save in this order: `form.html` right before showing the form, `intake.md` as soon as the answers arrive, `card.html` right before showing the card, and `changes.md` (one line is enough) as soon as the card is answered. The time between those pairs is the person's, and doesn't count against any step.

## Asking rules

Questions cost the person time, so each one has to earn its place:
- Ask only when the answer changes the plan.
- Max 3 questions per checkpoint after the intake form, in one batch, multiple choice built from the profile, with the recommended option marked.
- If the request, an attachment, or `guidelines/` already answers it, skip the question and state the assumption.
- If nobody answers, use the recommended options and list them under Assumptions in the plan.
- Never ask about chart library or styling; `guidelines/style.md` decides those.
- Never show internal ids or persona-style labels to the person; use the form's words from `guidelines/goals.md`.
