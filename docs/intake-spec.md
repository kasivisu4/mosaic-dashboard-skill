# Dashboard intake and confirmation

Use this section at the start of every dashboard request, before planning or querying.
Goal: capture intent with the fewest possible questions, then show the user your read
before building.

## 1. Infer first

Read the user's first message and any attachments. Fill in as many of these as you can
WITHOUT asking:

| Field | Values | Inferred from |
|---|---|---|
| goal (1–2) | answer, spec, explore, monitor, present | "why / what changed / which" → answer; names charts, columns, filters → spec; data with no question, "what's interesting" → explore; "track / daily / keep an eye on" → monitor; "for leadership / board / client", "show X how…" → present |
| cadence | one-time, weekly, monthly, daily | "every morning", "monthly review", "quick look" |
| request | free text | the message itself |
| success_criteria | free text | casual statements count: "I just need to see the top drivers fast" → "top drivers visible at a glance". Capture in every mode; ask for it only in Guided/Deep |
| data | file or location | attachments, connectors, named tables |
| glossary | term = definition | business terms that don't match column names |
| reconcile flag | on/off | "reconcile", "match finance / X report", "official", "audit", "board pack", audience = clients/regulators |
| audience | me, team, leadership, clients/regulators | "for my VP", "for the board", "for the auditors" |
| review_depth | quick, guided, deep | see section 4 |

If the user pasted or forwarded an original request (Slack, email, ticket), extract from
it first: goal, audience, cadence, metrics, terms, deadlines. It outranks your own guesses,
and every field it answers is dropped from the form.

Short-circuit rules:
- If goal = spec (request names specific charts/columns/filters): skip the form, skip the
  story, build exactly what was asked. List any assumptions after building.
- If everything needed is known: skip the form and go to step 3.
- Never ask for something already answered or attached.

## 2. Show the intake form (only the missing questions)

Render an inline elicitation form (load the visualizer's `elicitation` module first).
Header: "Dashboard details". Include ONLY the groups whose field is still unknown, in
this order:

1. goal — "What should this dashboard help with? Pick one or two."
   Cards (multi-select), each with an icon and subtitle:
   - Answer a question — "Why did X change?"
   - I know what I want — "I'll describe the charts"
   - Explore my data — "Show me what's interesting"
   - Keep an eye on it — "Spot issues early"
   - Make a case — "Tell a clear story"
2. cadence — "How often will it be used?"
   Pills (single): One-time deep dive · Weekly review · Monthly report · Daily check
3. request — "What's the ask? Paste the original request if you have it."
   Textarea. Placeholder: "Your own words, or paste the Slack message or email you got"
4. success_criteria — "This dashboard is useful if…"
   Textarea. Placeholder: "e.g. I can see the top 3 drivers of the drop in under 10 seconds"
5. data — "Where's the data?"
   File dropzone + textarea fallback. Placeholder: "or describe where it lives"
6. glossary — "Any terms with a specific meaning here?" (optional)
   Textarea. Placeholder: "e.g. NPA = 90+ days past due; active = 1+ transaction in 30 days"
   Show it only when the request or data contains business terms that don't map to
   columns, or the domain is regulated (lending, banking, insurance, healthcare).
7. audience — "Who will look at it?"
   Pills (multi): Just me · My team · Leadership · Clients or regulators
8. review_depth — "How much should I check with you before building?"
   Pills (single), NOTHING preselected: Just build it · Check assumptions first ·
   Full review with SQL

Rules:
- Phrase every prompt as a question, never a field label.
- Never use persona names (Analyst, Monitor, Executive…) in anything the user sees.
- Do not use sliders or preselected controls. A value equal to a control's default is
  NOT an answer — ignore it when inferring intent.

Fallbacks, in order:
- Inline form unavailable → use the structured question tool (max 4 questions, 2–4
  options each); ask goal, audience and review_depth; take request/data from chat.
- No structured question tool → ask the same questions as a short numbered list.

## 3. Parse the answers

Answers arrive as one line, e.g.
`Dashboard details — Goal: Answer a question, Make a case · Cadence: Monthly · …`

- If the form was skipped, OR both goal and request are empty: treat it as a skip.
  Fall back to the first chat message; if that has no intent either, ask ONE plain
  question: "What should this dashboard help with?" Do not re-show the full form.
- Merge answers with what you inferred in step 1. Answers win over inference.
- Two goals → layered dashboard: first goal on top, second underneath
  (e.g. answer + present = headline answer, then annotated story).
- Glossary terms present → domain flag ON: confirm each definition before computing.

## 4. Decide review depth

If the user chose it, use that. Otherwise infer:
- deep: reconcile flag ON, domain jargon not in the schema, research-style asks
  (when the reconcile flag is ON, also turn the domain flag ON)
- quick: goal = spec, casual phrasing, audience = just me
- guided: anything else that is ambiguous

| Checkpoint | Quick | Guided | Deep |
|---|---|---|---|
| Data check | assumed, listed | asked | asked + full profile |
| SQL review | — | — | asked |
| Story check | assumed, listed | asked | asked |
| Refine | offered | offered | offered |

## 4b. Let cadence shape the layout

| Cadence | Density | Emphasis |
|---|---|---|
| Daily | sparse, glanceable | status vs target, exceptions list, last-updated stamp; few or no dense tables |
| Weekly | medium | week-over-week deltas, short trend, top movers |
| Monthly | medium–rich | period comparisons, drivers, short narrative annotations |
| One-time | rich | full investigation: drivers, distributions, narrative, detail tables |

When cadence and goal pull in different directions (e.g. daily + explore), keep the
goal's structure and apply the cadence's density.

## 5. Confirmation card

Guided/Deep: show this card BEFORE building. Quick: build first, then show the same
card as the "here's what I assumed" note.

Render an inline interactive card containing:
1. My read — one sentence in plain words, e.g. "A monthly answer-first dashboard for
   leadership: the headline cause of the Q3 delinquency rise up top, with the
   supporting story underneath." Below it, chips for goal, cadence, audience, depth.
2. Still unsure about — one line naming what you're confident on and what's fuzzy, e.g.
   "Clear on the goal and audience. Still unsure: the comparison period, and whether
   delinquency includes charge-offs." No numeric confidence scores. Omit the line if
   nothing is fuzzy.
3. Layout preview — a small wireframe SVG built by stacking one block per goal, in
   goal order:
   - monitor: status row (on/off track vs target) — always placed on top if present
   - answer: headline banner, 3 KPI cards, driver chart + trend chart
   - explore: filter bar, dense grid of distributions, detail table
   - present: annotated story section — always placed at the bottom if present
   - spec: the charts exactly as requested (no other blocks)
   Apply the cadence density from 4b. Example: answer + monitor = status row, then
   headline answer and drivers.
4. Assumptions — 3–5 rows (metric definitions, comparison periods, breakdowns,
   exclusions), each with a "Change" button that sends
   `Change assumption: <name>`. Put the fuzzy items from item 2 first.
5. Success criteria — if one was stated or captured, show it in one line
   ("Built for: top 3 drivers visible at a glance").
6. "I'd also like to know" — 1–3 optional question chips, drawn from the fuzzy items
   first, then targets, reconciliation source, refresh needs. Clicking one sends that
   question.
7. Actions — "Looks right, build it" as the strong primary button (filled), "Adjust" as
   the secondary (outlined).

## 6. Handle follow-ups narrowly

- `Change assumption: <name>` → ask ONE focused question about that assumption only
  (structured question tool preferred, 3–5 options plus the current value). Update that
  assumption; keep everything else. Do not restart intake or re-ask other fields.
- `Adjust the plan` → ask ONE open question: "What should change?" Do not reopen the
  form. Apply the answer as a diff to the current plan (goals, layout, assumptions),
  then re-render the confirmation card with the changes marked.
- Layout edits in words ("swap these sections", "make the drivers bigger") → update the
  preview and plan the same way.
- Requests that reference what's on screen ("make it last year", "why doesn't this match
  finance?") → modify the existing plan or dashboard; never rebuild from scratch.

## 7. After building

Check the result against success_criteria, if given, and say in one line whether it
meets it (e.g. "Top 3 drivers are in the first row — visible without scrolling").
