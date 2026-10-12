# Customizing the planner for your organization

The planner (`skills/planning-dashboard/`) is meant to be forked and adapted. Everything an organization should change lives in one folder, `guidelines/`. The rest is method and shouldn't need editing.

## What to edit

| File | Change it to… | Effect |
|---|---|---|
| `guidelines/goals.md` | the intake form's wording and icons, the words that signal each goal, the page blocks per goal, audience rules, cadence density, when to ask for a glossary | how the planner reads requests, what it asks, and what each page contains |
| `guidelines/metrics.md` | add approved definitions (e.g. "Active user = …") | the planner uses them without asking whenever the data has the columns |
| `assets/intake-form.html`, `assets/confirmation-card.html` | the questions' wording and the card's layout (option labels come from `goals.md`) | what the person sees during intake |
| `guidelines/timing.md` | your latency targets per step | every run's `README.md` compares its timing against them |
| `guidelines/dashboard.md` | the build stack (Mosaic + DuckDB + Observable Plot, D3 when needed), cross-filtering, filter and KPI rules, the color policy (suggested per dashboard, or your pinned brand colors), fonts, and stricter audience limits | how every page is built and how it looks |

## What not to edit (unless you know why)

| File | Why |
|---|---|
| `references/plan-format.md`, `scripts/plan_format.py` | the agreed plan format; executors depend on it. Change it only together with every executor, and bump `plan_version`. |
| `scripts/validate_plan.py`, `scripts/profile.py` | shared checks. Extend rather than loosen them. |
| `SKILL.md` | the workflow. Edit the description if your org uses different words for "dashboard". |

## Using a different executor

The planner ends at `plan.md` + data files. Any executor can build from them:
- **Another Claude skill:** read `plan.md`; [plan-spec.md](plan-spec.md) is the contract. `building-dashboard-mosaic` is a working example.
- **A program:** parse with `scripts/plan_format.py` (`parse(text)` returns a dict), or follow the spec.
- **A person or BI tool:** hand them `plan.md`. It reads as a brief.

## After customizing

1. Run `python skills/planning-dashboard/scripts/validate_plan.py examples/orders-dashboard/plan.md` to make sure the format still validates.
2. Try a few real requests from your org in a test session (see the README's "Interactive testing").
3. Package the skill and share it (README).

## Ideas not built yet

- **Suggestions from earlier choices.** The intake form tags nothing as "Suggested" today: goal, cadence, audience and review depth can't be guessed from the data. Once the planner remembers a person's earlier answers (for example, the same person usually picks "Weekly review" for "My team"), those could be shown as suggestions, still never preselected.
