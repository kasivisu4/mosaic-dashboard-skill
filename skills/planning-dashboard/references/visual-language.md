# Visual language: know the rules, break the conventions, keep the truth

To break a system you first have to know its rules. This file has three parts:

1. **The conventional playbook:** the chart everyone reaches for, for each kind of question. Know it so you can recognize the default when you're about to draw it.
2. **Beyond the default:** what to draw instead. Pages built by this skill don't use the conventional form for a question unless no alternative shows the finding better (then say why in the `~ draw:` line).
3. **Rules you never break:** the honesty rules. Conventions are taste and can be broken; these are about truth, and an unusual chart needs them more, not less.

The plan's forms (`trend`, `bar`, `histogram`, `scatter`, `exceptions`) say what *question shape* a story line answers. They aren't drawing instructions. The `~ draw:` line under each chart says how it is drawn.

## Contents
- Part 1. The conventional playbook
- Part 2. Beyond the default
- Part 3. Rules you never break
- Part 4. Before sharing: the honesty pass

## Part 1. The conventional playbook

These are the defaults taught in every dataviz course. They are correct and safe, and that's the problem: a page made only of them looks like every other dashboard, and readers skim past it.

| Question | Conventional form | Its rules |
|---|---|---|
| Change over time | line chart (bars for few periods) | time on x, left to right; one y-axis; ≤ 5 lines |
| Ranking | sorted horizontal bar | zero baseline; sorted by value; labels on the left |
| Part of a whole | pie / donut, stacked bar | ≤ 5 slices; parts sum to 100% |
| Mix over time | stacked area, 100% stacked bar | the baseline series is the only one easy to read |
| Distribution | histogram, box plot | equal bins; bin width stated |
| Relationship | scatter plot | ≥ 30 points; both axes labelled with units |
| Two dimensions × a measure | heatmap / table | sequential color; legend with a scale |
| A single number | KPI tile | value, unit, comparison |
| Flow between states | Sankey | widths proportional to the flow |
| Geography | choropleth | normalized values, not raw counts |

## Part 2. Beyond the default

These are **examples, not limits**: start from the brief's concepts (`question-brief.md` §3), and use this table to check you aren't drawing the default, not as the list to pick from. Every page includes at least one invented form. Pick what makes *this* finding obvious; a novel form that hides the finding is worse than the default. Each comes with how to build it here (Plot through vgplot when it can, D3 as a Mosaic client when it can't; see [mosaic-tech.md](mosaic-tech.md) and [motion.md](motion.md)).

| Question | Instead of | Draw | Why it works | Build |
|---|---|---|---|---|
| Change over time | line chart | **Horizon chart** (many series, compact) | 10+ series readable in the space of 2 lines; peaks pop | D3 |
| | | **Annotated timeline with event markers**, the line muted and the moments lit | the story is in the moments, not the wiggle | Plot + D3 labels |
| | | **Calendar heatmap** (weeks × weekday or a 365-day grid) | shows rhythm *and* breaks (outages, launches) at once | Plot `cell` or D3 |
| | | **Cycle plot** (one mini-line per hour/weekday across the period) | separates season from trend | Plot `fx` |
| Ranking | sorted bar | **Dot plot / lollipop** with the average or target as a rule | less ink, the gap to the reference is the message | Plot |
| | | **Ranked list with inline bars and deltas** | readable numbers and shape together | HTML client |
| Rank over time | multi-line | **Bump chart** (rank on y, time on x) | crossings, the moment one overtakes another, are the story | D3 |
| | | **Slope chart** (two periods only) | before/after in one glance | Plot |
| Part of a whole | pie / donut | **Waffle (10×10 unit grid)** | each square = 1%; counts, not angles | D3 |
| | | **Single 100% bar with direct labels** | one length to read | Plot |
| Mix over time | stacked area | **Small multiples** on a shared y-scale, each with the total as a grey ghost | every series has a true baseline | Plot `fy` |
| | | **Streamgraph**, only for mood, never for reading values (label it so, and add a readable view) | shows flow and turnover of many categories | D3 |
| | | **Share-shift / slope of shares** between two periods | the change in mix is the message | Plot |
| Distribution | histogram | **Beeswarm / dot strip** (each mark a unit) | shows real units and outliers; no bin choice | D3 force or Plot `dodge` |
| | | **Ridgeline** (one density per category, overlapping) | compares many distributions in one view | D3 |
| | | **Quantile dot plot** (20 dots = 5% each) | intuitive frequency | D3 |
| Relationship | scatter | **Connected scatter** (points joined in time order) | how two measures moved *together* over time | Plot `line` + `dot` |
| | | **Hexbin / density** for > 5k points | no overplotting | Plot `hexbin` |
| Two dims × measure | heatmap | **Heatmap with marginal bars** (row and column totals) | the matrix plus where the totals come from | Plot `cell` + bars |
| | | **3D terrain that rises out of the heatmap** (orbit, hover values) | the shape of the whole surface at once: ridges, holes, the outage | three.js (`stage.md` §5) |
| | | **Radial clock (24 h around a circle)**, only for cyclic dims like hour of day | a cycle drawn as a cycle | D3 |
| Single number | KPI tile | **Number with its own sparkline and reference tick** | the number plus its trajectory | HTML + D3 |
| | | **Count-up hero number** with a sentence (motion: reveal) | the hook lands as the page opens | HTML + D3 |
| Flow | Sankey | **Alluvial between periods** (category membership from period to period) | shows who switched | D3 |

**Fresh every time.** Choose from this table for the data and the story in front of you. Don't repeat the previous dashboard's forms because they worked there, and don't reuse its code as a template: a different dataset deserves a different look.

**Show reels.** `scripts/design_seed.py` picks chains of forms from this table for each run; [show-reel.md](show-reel.md) morphs one set of marks through them.

**Morphs.** Where two forms in this table are both honest views of the same data (waffle and unit bars, radial clock and bars, rank and share, calendar and timeline), a card can morph between them: `motion.md`, section 6.

Composition ideas that beat a grid of equal cards:
- **Hero + supporting:** one large primary surface (the hook) with 2–4 smaller angles under it.
- **Linked views:** a time brush along the page's bottom edge that drives every view above it.
- **Focus + context:** a small overview with a detail view of the brushed range; or a hero that keeps the whole period and shows the time filter as a band (see `motion.md`, section 5).
- **Scrolly sections:** each angle as a section with one sentence, revealed in reading order (motion: reveal).

## Part 3. Rules you never break

Breaking a convention is design. Breaking one of these is deception, whatever the chart looks like. They apply to every form above.

**Scales and baselines**
1. **Length and area encodings start at zero.** Bars, lollipops, areas, waffles, stream thickness. If the variation is small, show the change itself (a delta chart), don't truncate.
2. **Positions may start elsewhere, and say so.** A line or dot axis may zoom in; label the axis range and never pair it with bars.
3. **Areas are proportional to values.** Circle *area*, not radius, maps to the value (`d3.scaleSqrt`). No decorative 3D or perspective; a 3D scene needs three data axes, an orbit camera, zero-based linear height and exact values on hover (`stage.md` §5).
4. **One axis per measure.** No dual y-axes; use two aligned panels on the same x.
5. **Shared scales across small multiples** unless the point is shape, and then say "independent scales" on the chart.
6. **Log scales are labelled "log scale"** on the axis, with ticks at real values.
7. **Radial forms:** radius encodes nothing by itself unless it's proportional (sqrt); angle only for cyclic dimensions (hour, month). Never a radar or a radial bar to rank things.

**Data honesty**
8. **No cherry-picked windows.** The default view shows the full period. A narrower window is chosen by the reader, or labelled with why ("since the September peak").
9. **Partial periods are marked.** A first or last bucket with fewer days is labelled or shown hatched, never compared as if whole.
10. **Rates show their denominator** somewhere (tooltip or note), and averages over aggregated rows are ratios of sums.
11. **Missing data is a gap,** not interpolated, not zero.
12. **Smoothing is labelled** (window size), and no number is read off a smoothed line.
13. **Streamgraphs, wiggle offsets and other value-hiding forms** are for shape only: never the only view of a number the title states.

**Color and attention**
14. **Color never carries meaning alone;** pair it with a label, position or icon.
15. **The highlighted thing is what the title claims.** Don't spotlight a series the title doesn't mention.
16. **Annotations state facts with their numbers;** causes are stated only when known ("cause unknown" otherwise).

**Motion**
17. **Animation never changes a scale silently.** When an axis rescales on a filter, the axis animates with the marks, or the scale is fixed.
18. **Every animated state is a true state.** Tweens interpolate between real values; no bounce or overshoot that shows values the data doesn't have.
19. **Reduced motion is respected by default** (`prefers-reduced-motion`): the end state appears instantly, and a visible Motion switch lets the viewer turn animation on (`motion.md`, The Motion switch).

## Part 4. Before sharing: the honesty pass

For every chart on the page, write one line in `5-handoff/handoff.md` under "Honesty pass": the chart's title, the rules from Part 3 that apply to it, and how it meets each. A chart that fails a rule is fixed before the link is shared, not footnoted.

Then look at the page as the reader would and ask: if someone took a screenshot of any one chart out of context, would it still tell the truth? If not, the missing context (period, scale note, denominator) goes onto that chart.
