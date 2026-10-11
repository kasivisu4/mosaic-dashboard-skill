# Intake and confirmation

Capture intent with the fewest questions, then show the person your read before anything is built. The wording, signals and page blocks come from [../guidelines/goals.md](../guidelines/goals.md); this file is the method.

## Contents
- 1. Infer first
- 2. The intake form (only missing questions)
- 3. Parse the answers
- 4. Decide review depth
- 5. The confirmation card
- 6. Follow-ups
- 7. After building

## 1. Infer first

Read the first message and any attachments. Fill in every field you can WITHOUT asking:

| Field | Values | Inferred from |
|---|---|---|
| goals (1–2) | answer, spec, explore, monitor, present | the signals in `guidelines/goals.md` |
| cadence | one-time, daily, weekly, monthly | "every morning", "monthly review", "quick look" |
| request | free text | the message itself |
| success_criteria | free text | casual statements count: "I just need to see the top drivers fast" → "top drivers visible at a glance". Capture it in every depth; ask for it only in guided/deep |
| data | file or location | attachments, connectors, named tables, paths |
| glossary | term = definition | business terms that don't match column names |
| reconcile | on/off | "reconcile", "match finance / the X report", "official", "audit", "board pack", audience = clients |
| audience | me, team, leadership, clients | "for my VP", "for the board", "for the auditors" |
| review_depth | quick, guided, deep | section 4 |

If the person pasted or forwarded an original request (Slack, email, ticket), extract from it first: goal, audience, cadence, metrics, terms, deadlines. It outranks your own guesses, and every field it answers is dropped from the form.

Short-circuits:
- **goal = spec** (the request names specific charts, columns or filters): skip the form and the story; plan exactly what was asked and list assumptions after building.
- **Everything needed is known:** skip the form, go to step 3.
- Never ask for something already answered or attached.

## 2. The intake form (only missing questions)

Show only the groups whose field is still unknown, in this order, under the header **"Dashboard details"**. Every prompt is a question, never a field label. Never show persona-style names (Analyst, Executive, Monitor…) to the person. Nothing is preselected, and a control left at a default is not an answer.

| # | Ask | Format | `data-name` → values |
|---|---|---|---|
| 1 | What should this dashboard help with? Pick one or two. | cards, multi-select, icon + subtitle from `goals.md` | `goal` → `answer`, `spec`, `explore`, `monitor`, `present` |
| 2 | How often will it be used? | pills, single | `cadence` → `one-time`, `weekly`, `monthly`, `daily` |
| 3 | What's the ask? Paste the original request if you have it. | textarea: "Your own words, or paste the Slack message or email you got" | `request` |
| 4 | This dashboard is useful if… | textarea: "e.g. I can see the top 3 drivers of the drop in under 10 seconds" | `success_criteria` |
| 5 | Where's the data? | file dropzone + textarea: "or describe where it lives" | `data`, `data_text` |
| 6 | Any terms with a specific meaning here? (only when `goals.md` says so) | textarea: "e.g. NPA = 90+ days past due; active = 1+ transaction in 30 days" | `glossary` |
| 7 | Who will look at it? | pills, multi-select | `audience` → `me`, `team`, `leadership`, `clients` |
| 8 | How much should I check with you before building? | pills, single, nothing preselected | `review_depth` → `quick`, `guided`, `deep` |

Pill and card labels come from `goals.md`; `data-value` is always the id, so answers parse the same whatever the wording. Use no sliders.

**How to show it**, the first that's available:
1. **Inline form widget** (e.g. the visualizer's `show_widget`): load its `elicitation` module with its `read_me` first. Don't write the form yourself; generate it, so it's fast and identical every time. On the first turn that's one command:
   ```bash
   python scripts/start_run.py out/<name> <data file> --skip <fields already answered> [--glossary]
   ```
   Pass the printed HTML to the widget unchanged. (`python scripts/intake_form.py --skip ... --data <file>` prints the same form without starting a run, e.g. to show it again.)

   A field you're confident about goes in `--skip` and isn't asked; otherwise ask it plainly. Don't guess goal, cadence, audience or depth for the person: the data can't tell you those. What the data *can* suggest is the ask: "What's the ask?" offers 2–3 questions built from the data's own columns. Use `--hint "success_criteria=e.g. ..."` when the request suggests better example text than the data does. Fields: `goal`, `cadence`, `request`, `success_criteria`, `data`, `audience`, `review_depth`; add `--glossary` only when `goals.md` says to ask it. Exit code 2 means nothing is left to ask: skip the form.
2. **Structured question tool** (e.g. `AskUserQuestion`): at most 4 questions of 2–4 options. Ask goal, audience and review_depth; take request and data from the chat.
3. **Neither:** ask the same questions as a short numbered list.

## 3. Parse the answers

The form's answers arrive as one line, e.g. `Dashboard details — Goal: answer, present · Cadence: monthly · Audience: leadership · …`

- Skipped form, or both goal and request empty → fall back to the first message. If that has no intent either, ask ONE plain question: "What should this dashboard help with?" Don't show the form again.
- A picked ask arrives as `Suggested ask: <text>`; treat it as the request (and a typed request, if both are given, wins).
- Merge the answers with what you inferred; answers win.
- Two goals → a layered page: the first goal's block on top, the second underneath (`goals.md` placement rules apply).
- Glossary terms given → confirm each definition against the data before computing with it, and write them into the plan's `## Data` lines.
- Audience `clients` → reconcile on.

## 4. Decide review depth

If the person chose it, use it. Otherwise:
- **deep:** reconcile on, domain jargon not in the schema, research-style asks.
- **quick:** goal = spec, casual phrasing, audience = just me.
- **guided:** anything else that is ambiguous.

| Checkpoint | quick | guided | deep |
|---|---|---|---|
| Data check | assumed, listed | asked | asked + full profile |
| SQL review | — | — | asked |
| Confirmation card | after building, as "here's what I assumed" | before building | before building |
| Refine | offered | offered | offered |

## 5. The confirmation card

After profiling and the data check, show the card (guided/deep: before writing the plan; quick: after building). Don't write the card's HTML yourself. Write a small `card.json` (fields below; the format is in `scripts/confirmation_card.py`'s help) and generate it:

```bash
python scripts/confirmation_card.py card.json
```

```json
{"read": "...", "goals": ["answer", "present"], "cadence": "monthly", "audience": ["leadership"],
 "review_depth": "deep", "unsure": "...", "assumptions": [{"name": "...", "value": "..."}],
 "changed": [], "success_criteria": "...", "questions": ["..."], "after_build": false}
```

Pass the printed HTML unchanged to the inline widget (load the visualizer's `mockup` module first). Without a widget, show the same content as a short Markdown block followed by a structured question with the same choices. Use ids in `card.json`; the script turns them into the form's words.

1. **My read:** one plain sentence, e.g. "A monthly answer-first dashboard for leadership: the headline cause of the Q3 rise up top, with the supporting story underneath." Below it, chips for goals, cadence, audience, depth (in the form's words, never ids or persona names).
2. **Still unsure about:** one line naming what's clear and what's fuzzy. No numeric confidence. Omit it if nothing is fuzzy.
3. **Layout preview:** a small wireframe SVG stacking one block per goal from `goals.md`, at the cadence's density.
4. **Assumptions:** 3–5 rows (metric definitions, comparison period, breakdowns, exclusions), fuzzy items first, each with a **Change** button that sends `Change assumption: <name>`.
5. **Built for:** the success criteria in one line, if any.
6. **I'd also like to know:** 1–3 optional question chips (fuzzy items first, then targets, reconciliation source, refresh needs); a click sends the question.
7. **Actions:** "Looks right, build it" (filled, primary) sends `Looks right, build it`; "Adjust" (outlined) sends `Adjust the plan`.

The generated card's buttons send exactly those texts. After a change, regenerate it with the assumption's name in `changed`.

## 6. Follow-ups

- `Change assumption: <name>` → ONE focused question about that assumption (structured question tool preferred: 3–5 options plus the current value). Update it, keep everything else, show the card again with the change marked.
- `Adjust the plan` → ONE open question: "What should change?" Apply the answer as a diff to goals, layout and assumptions, then show the card again with the changes marked. Don't reopen the form.
- Layout edits in words ("swap these sections", "make the drivers bigger") → update the preview and the plan the same way.
- Requests about what's on screen ("make it last year", "why doesn't this match finance?") → change the existing plan or dashboard; never start over.

## 7. After building

Check the result against success_criteria, if given, and say in one line whether it's met, e.g. "Top 3 drivers are in the first row, visible without scrolling."
