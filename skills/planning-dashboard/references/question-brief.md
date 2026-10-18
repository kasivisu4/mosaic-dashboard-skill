# Question brief: from one question to angles worth drawing

A person asks one question, but a page that holds attention answers the question behind it as well. Before laying anything out, turn the request into a short written brief: who the reader is, what they need, why, and how they'll read the page. Then turn the question into supporting questions, each with an angle that's worth seeing. Save it as `2-intake/brief.md` right after `intake.md`.

The brief is a document for the person and for whoever builds the page: decisions and their reasons in plain sentences. Write it from the intake and the profile; don't paste working notes into it.

## Contents
- 1. Reader: what, why, how
- 2. Supporting questions
- 3. Angles
- 4. Pick the page's angles
- 5. Template

## 1. Reader: what, why, how

Answer each in one or two sentences, from the request, the intake answers and the profile. Mark anything inferred with *(inferred)*.

| | Ask yourself | Example |
|---|---|---|
| **Who** | Who reads it, and what do they already know about this data? | Client analysts who know LLM serving but not this platform |
| **What** | What is the literal question, in the person's words? | How did volume, tokens, latency and model choice change over the year? |
| **Why** | What decision, belief or action does the answer feed? What would surprise them? | Choosing which model families to build on; a shift in model choice would matter more than raw volume |
| **How** | How will they read it: skim in 10 s, explore for 10 min, present to others? On what screen? | Opened once, explored for several minutes, screenshots shared in a deck |
| **Hook** | The one finding that earns their attention, with its number from the profile | Qwen went from 3% to 47% of requests in nine months |

The **hook** must be a computed number, not a guess. If the profile shows nothing surprising, say so; the hook is then the clearest answer to the literal question.

## 2. Supporting questions

Expand the question into 3–5 supporting questions the data can answer. Generate them with these lenses, and keep the ones whose answer would change what the reader believes or does:

| Lens | Question pattern |
|---|---|
| Change | When did it change, how fast, and was it a step or a drift? |
| Composition | Which parts make up the whole, and did the mix shift while the total stayed flat (or the reverse)? |
| Rank | Who leads, who rose, who fell, and when did the order flip? |
| Relationship | Does one measure move with another (volume vs. latency), and is the link only the mix? |
| Distribution | Is the average typical, or do a few extremes drive it? |
| Rhythm | Is there a cycle (hour, weekday, season) or a break in it (an outage, a launch)? |
| Contrast | How does the selected slice differ from the rest, or this period from the last? |

Every supporting question needs columns that exist in the profile. Drop any that would need data the file doesn't have, and note the gap under Limitations in the brief.

## 3. Angles

### Concepts first

Lists anchor: whatever a catalog names is what you reach for. So before choosing any visual, sketch **five concepts for the hook** that differ in kind, not in color: different mark units, different metaphors, different layouts. At least one must be **invented**: a form no catalog in this skill names, derived from this data's shape (what one mark could stand for, what physical process the change resembles, what the reader already knows how to read). Use the design seed's `provocations` as prompts. Write each concept in one line, then pick on three tests: the finding is obvious in five seconds, every honesty rule holds, and it is something the reader hasn't seen in a dashboard before. Record all five under "Concepts considered" in the brief, with why the winner won. [d3-toolkit.md](d3-toolkit.md) is the vocabulary to build any of them, not a list to choose from.

An **angle** is the way of looking that makes an answer obvious at a glance: the comparison, the frame, and the visual. For each supporting question write:

- **Answer preview:** the finding with its number, computed with DuckDB (it becomes the chart's finding-title).
- **Comparison:** what is set against what (before/after, part/whole, this/rest, rank/time).
- **Visual:** the conventional form you are *not* using, and the one you are (from the concepts, a catalog in [visual-language.md](visual-language.md), or invented), with the reason.
- **Motion:** what moves and why, from [motion.md](motion.md), or "none".
- **Honesty check:** the one rule from `visual-language.md` most at risk with this visual, and how the design keeps it.

## 4. Pick the page's angles

Rank the angles by how much each one changes the reader's picture, then keep what the Style Profile's density allows. The hook's angle is the page's primary surface (style-system principle 1). Each kept angle becomes one story line in the plan with a `~ draw:` line. The ones left out go under "Angles not drawn" in the brief, with the reason.

On the confirmation card (guided and deep), the kept angles appear as one assumption row: `Angles: <hook angle>; <angle 2>; …`. Changing it gets ONE question with the dropped angles as options.

## 5. Template

```markdown
# Brief: <short name>

## Reader
- Who: …
- What: …
- Why: …
- How: …
- Hook: … (<number>, from <query>)

## Concepts considered (for the hook)
1. <concept in one line> — <why not / why>
2. …
5. <invented form> — …
Chosen: <n>, because …

## Supporting questions
1. <question> (lens: …)
   - Answer preview: …
   - Comparison: …
   - Visual: <unconventional form> instead of <conventional form>, because …
   - Motion: …
   - Honesty check: …
2. …

## Angles not drawn
- <question>: <why it was left out>

## Limitations
- <questions the data can't answer, and why>
```
