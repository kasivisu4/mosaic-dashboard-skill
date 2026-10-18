# Timing budget

> **Customize this file** with your organization's latency targets. `scripts/run_folder.py summary` reads the table below and compares every run against it; keep the column layout. Times are seconds of system work: time spent waiting for the person (filling in the form, reading the card) is measured separately and never counts against a step.

| Step | Folder | What the system does | Target (s) | Max (s) |
|---|---|---|---|---|
| 1. Profile | `1-profile` | quick look (column types on a sample) before the form; the full profile runs in the background | 1.5–4 | 8 |
| 2. Intake form | `2-intake` | infer from the first message, build the form from the quick look, show it (or skip it) | 0.3–0.8 | 1.2 |
| 3. Layout and card | `3-layout` | data definitions, page blocks, finding-titles, and the confirmation card | 4–10 | 17 |
| 4. Plan | `4-dashboard` | final plan, SQL, export, validation | 2–6 | 10 |
| 5. Hand-off | `5-handoff` | build the dashboard (charts, queries, layout) and share the link | 3–12 | 20 |

## Rules that keep the first dashboard fast

- **Nothing before the form but `start_run.py`.** On the first turn, run it and show the form it prints. Its quick look (well under a second; about 2 s for billions of rows) is the only data read before the form. Don't list folders, check file sizes, read schemas or metadata, run other queries, or read other references first: the script handles any file size (see SKILL.md).
- **Profile while the person fills in the form.** `scripts/start_run.py` starts the full profile in the background as it prints the form, so the profile is ready by the time the answers arrive.
- **No separate data round.** Questions about the data (definitions, exclusions) go on the confirmation card as assumptions with Change buttons, not in a round of their own.
- **Quick depth builds first.** No card at all; what was assumed goes in the plan's Assumptions section.
- **Link before review.** Give the person the dashboard link as soon as the page is built; run the browser review after, and report anything it finds as a follow-up.
- **Scripts, not prose.** Generate the form, card, plan checks, and page with the scripts; don't hand-write what a script produces.
