# Data story

## Finding-titles
- A title states what the data shows: "Signups doubled after the March launch", not "Signups over time".
- Compute every number in a title with DuckDB before writing it.
- If there is no clear finding, use a neutral descriptive title. Never invent one.
- A "from X to Y" claim compares the first and last *full* periods. Starting from a peak or a low is a cherry-pick unless the title names it as one ("from its September low"), and a partial period is never an endpoint. Check the claim over the full span before writing it: a dramatic change measured from an extreme often disappears.

## Page structure from goals
Stack the blocks for the plan's goals from `guidelines/goals.md` (monitor on top, present at the bottom, otherwise goal order), at the cadence's density. Within a block:
- **answer:** the takeaway paragraph states the headline answer; the driver bar comes before the trend.
- **monitor:** KPIs with targets first, then the exceptions list; nothing that needs reading closely.
- **explore:** breadth over depth: several small distributions and breakdowns, menus on every useful dimension.
- **present:** one finding per chart, each with a `>` narrative line and an `@` annotation at the key moment.
- **impact:** open on the hook as an animated hero; then each supporting angle in an unconventional form, one key moment annotated per chart; the title states the finding, the visual makes the reader want to check it.
- **spec:** exactly the charts asked for, in the order asked, titled plainly if the person didn't title them.

## Chart form from column classes

These pick the plan *form* (the question shape). How it's drawn is the `~ draw:` line, chosen with [visual-language.md](visual-language.md), and the brief's angles ([question-brief.md](question-brief.md)) decide which forms the page needs.
| Data | Plan form |
|---|---|
| date × measure | `trend` |
| dimension × measure | `bar` (ranked) |
| one measure's spread | `histogram` |
| categories breaking a limit | `exceptions` |
| measure × measure | `scatter` |

No date column means no `trend`; lead with the strongest breakdown instead. Rating-like columns (few distinct small integers) use `avg()` or a `histogram`, never `sum()`.

## On the confirmation card
The assumptions on the card (`intake.md` section 5) are the story check: offer at most one swap or addition there, built from dimensions the profile found.
