# Timing budget

> **Customize this file** with your organization's latency targets. `scripts/run_folder.py summary` reads the table below and compares every run against it; keep the column layout. Times are seconds of system work: time spent waiting for the person (filling in the form, reading the card) is measured separately and never counts against a step.

| Step | Folder | What the system does | Target (s) | Max (s) |
|---|---|---|---|---|
| 1. Profile | `1-profile` | quick look (column types on a sample) before the form; the full profile runs in the background | 1.5–4 | 8 |
| 2. Intake form | `2-intake` | infer from the first message, build the form from the quick look, show it (or skip it) | 0.3–0.8 | 1.2 |
| 3. Data check | `3-data-check` | quality checks, missing values, outliers, term matching | 1–3 | 5 |
| 4. Layout and story | `4-layout` | structure, chart forms, finding-titles, narrative skeleton | 2–5 | 8 |
| 5. Confirmation card | `5-confirm` | "My read", wireframe, assumptions, optional questions | 1–2.5 | 4 |
| 6. Plan | `6-dashboard` | final plan, SQL, export, validation | 2–6 | 10 |
| 7. Hand-off | `7-handoff` | build the dashboard (charts, queries, layout) | 3–12 | 20 |
| 8. Review | `8-review` | success-criteria check and refine suggestions | 0.8–2 | 3 |

## Rules that keep the first dashboard fast

- **Nothing before the form but `start_run.py`.** On the first turn, run it and show the form it prints. Its quick look (well under a second) is the only data read before the form; don't run other queries or read other references first.
- **Profile while the person fills in the form.** `scripts/start_run.py` starts the full profile in the background as it prints the form, so the profile is ready by the time the answers arrive.
- **Overlap the data check with profiling.** Draft data-check questions from the profile as soon as it lands; don't wait for a separate pass.
- **Quick depth builds first.** No card before building; the card comes after, as "here's what I assumed".
- **Link before review.** Give the person the dashboard link as soon as the page is built; run the browser review after, and report anything it finds as a follow-up.
- **Scripts, not prose.** Generate the form, card, plan checks, and page with the scripts; don't hand-write what a script produces.
