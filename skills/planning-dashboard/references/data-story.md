# Data story

## Finding-titles
- A title states what the data shows: "Signups doubled after the March launch", not "Signups over time".
- Compute every number in a title with DuckDB before writing it.
- If there is no clear finding, use a neutral descriptive title. Never invent one.

## Page structure from goals
Stack the blocks for the plan's goals from `guidelines/goals.md` (monitor on top, present at the bottom, otherwise goal order), at the cadence's density. Within a block:
- **answer:** the takeaway paragraph states the headline answer; the driver bar comes before the trend.
- **monitor:** KPIs with targets first, then the exceptions list; nothing that needs reading closely.
- **explore:** breadth over depth: several small distributions and breakdowns, menus on every useful dimension.
- **present:** one finding per chart, each with a `>` narrative line and an `@` annotation at the key moment.
- **spec:** exactly the charts asked for, in the order asked, titled plainly if the person didn't title them.

## Chart form from column classes
| Data | Plan form |
|---|---|
| date × measure | `trend` |
| dimension × measure | `bar` (ranked) |
| one measure's spread | `histogram` |
| categories breaking a limit | `exceptions` |
| measure × measure | `scatter` |

No date column means no `trend`; lead with the strongest breakdown instead. Rating-like columns (few distinct small integers) use `avg()` or a `histogram`, never `sum()`.

## On the confirmation card
The layout preview and assumptions on the card (`intake.md` section 5) are the story check: show the blocks in order with their finding-titles, and offer at most one swap or addition, built from dimensions the profile found.
