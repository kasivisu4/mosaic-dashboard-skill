# Mosaic Dashboard Skill

A **dashboard planner** for Claude, with **swappable executors**.

Most dashboard tools go straight from a request to charts. This planner decides first, with the person: what the page should help with, who reads it, how often, and what the numbers mean. Then it writes a validated plan. An executor (a Claude skill, another program, or a BI tool) builds from that plan. Organizations adapt the planner by editing one folder, `guidelines/`.

New here? Start with [docs/how-it-works.md](docs/how-it-works.md). Customizing it? [docs/customizing.md](docs/customizing.md). Writing an executor? [docs/plan-spec.md](docs/plan-spec.md). Original design: [docs/brief.html](docs/brief.html) and [docs/intake-spec.md](docs/intake-spec.md).

## Status

| Part | State |
|---|---|
| `planning-dashboard` (planner) | Active. Five steps: profile, intake form fitted to the data, layout + confirmation card, validated plan (format v2), hand-off; run folders with timing |
| `building-dashboard-mosaic` (executor) | Parked. Builds pages from plans, but doesn't yet draw v2's KPI targets, exceptions lists, annotations or "last updated", and axis labels ignore the plan's number formats |

## How a run goes

Every run is recorded in `out/<name>/`, one numbered folder per step:

| Step | What happens | Saved in |
|---|---|---|
| 1. Profile | `start_run.py` takes a quick look at the data (well under a second, even for millions of rows) and starts the full profile in the background | `1-profile/` |
| 2. Intake | The "Dashboard details" form, built from that look: it asks only what the request didn't answer, and "What's the ask?" offers 2–3 questions this data can answer | `2-intake/` |
| 3. Layout and card | Page blocks for the chosen goals, with every number in a title computed by DuckDB, confirmed on one card: "My read", a layout preview, and the data definitions as assumptions with Change buttons (quick review: shown after building) | `3-layout/` |
| 4. Plan | Data exported, `plan.md` written and validated | `4-dashboard/` |
| 5. Hand-off | An executor builds the page; the link is shared right away | `5-handoff/` |

`run_folder.py summary` writes the run's `README.md`: each step's files and its time against the budget in `guidelines/timing.md`. Time spent waiting for the person doesn't count against any step.

## Layout

Follows the [Agent Skills spec](https://agentskills.io/specification) and the layout of [anthropics/skills](https://github.com/anthropics/skills):

```
mosaic-dashboard-skill/
├── .claude-plugin/marketplace.json     # two installable plugins: planner + Mosaic executor
├── docs/                               # how-it-works, customizing, plan-spec, intake-spec, brief
├── examples/orders-dashboard/          # plan.md → index.html, end to end
├── tools/sync_plan_format.py           # keeps the shared plan parser identical in every skill
└── skills/
    ├── planning-dashboard/             # THE PLANNER: ends at a validated plan + data
    │   ├── SKILL.md                    # speed rules, workflow checklist, run folder, asking rules
    │   ├── guidelines/                 # ← organizations edit these
    │   │   ├── goals.md                # form wording, goal signals, page blocks, audiences, cadence
    │   │   ├── metrics.md              # approved metric definitions
    │   │   ├── style.md                # brand colors per style role, fonts, stricter audience limits
    │   │   └── timing.md               # latency budget per step
    │   ├── references/                 # method: intake, understand-data, data-story, interaction,
    │   │                               #   style-system, destinations, plan-format (the contract)
    │   ├── assets/                     # intake-form.html, confirmation-card.html, plan-template.md
    │   ├── scripts/
    │   │   ├── start_run.py            # first turn in one command: quick look, background profile, form
    │   │   ├── quick_look.py           # column types on a sample, for the form
    │   │   ├── profile.py              # full DuckDB profile (CSV/TSV/Parquet/JSON/Excel, --columns)
    │   │   ├── intake_form.py          # the form, fitted to the data
    │   │   ├── confirmation_card.py    # the card, from a small card.json
    │   │   ├── validate_plan.py        # checks a plan before handing it off
    │   │   ├── run_folder.py           # step folders and the run summary with timing
    │   │   ├── plan_format.py          # shared plan parser
    │   │   └── goal_tables.py          # reads guidelines/goals.md
    │   └── evals/                      # test requests (not packaged)
    └── building-dashboard-mosaic/      # ONE EXECUTOR: plan → Mosaic + DuckDB-WASM page
        ├── SKILL.md
        ├── assets/mosaic-dashboard.html
        ├── references/                 # mosaic.md (engine), review.md (checklist)
        ├── scripts/                    # build_page.py, plan_format.py (synced copy)
        └── evals/
```

## Install

**Claude Code** (from a local clone):

```bash
/plugin marketplace add <path to this repo>
```

```bash
/plugin install planning-dashboard@mosaic-dashboard-skills
```

```bash
/plugin install building-dashboard-mosaic@mosaic-dashboard-skills
```

Or link the skill folders into a project's `.claude/skills/` to test them there.

**claude.ai:** package each skill with the skill-creator skill ("package skills/planning-dashboard"), then upload the `.skill` file in Settings → Capabilities → Skills.

Requires Python with `duckdb`:

```bash
pip install duckdb
```

## Try it

Make the sample data, then start a run the way the skill does on its first turn:

```bash
python skills/planning-dashboard/evals/make_fixtures.py
```

```bash
python skills/planning-dashboard/scripts/start_run.py out/try skills/planning-dashboard/evals/files/orders.parquet --skip data
```

That prints the intake form and fills `out/try/1-profile/` and `out/try/2-intake/`.

The end-to-end example (plan → page):

```bash
python examples/orders-dashboard/make_data.py
```

```bash
python skills/planning-dashboard/scripts/validate_plan.py examples/orders-dashboard/plan.md
```

```bash
python skills/building-dashboard-mosaic/scripts/build_page.py examples/orders-dashboard/plan.md
```

```bash
python -m http.server 8000
```

Then open http://localhost:8000/examples/orders-dashboard/.

## Developing

- Rules for editing the skills are in [CLAUDE.md](CLAUDE.md): stay domain-agnostic, keep org choices in `guidelines/`, change the plan format and its parser together.
- After changing `plan_format.py`, run `python tools/sync_plan_format.py`.
- Test requests live in `skills/*/evals/evals.json`; run them with the skill-creator skill.
