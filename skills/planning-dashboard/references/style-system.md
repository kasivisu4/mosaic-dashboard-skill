# Style system

Style isn't a palette. For every dashboard the planner derives a **Style Profile** from three signals (goal, audience, data character) and writes it into the plan's `## Style` section. The executor renders the profile; it never picks its own look. How pages are built, the color policy and any stricter audience limits are the organization's, in [../guidelines/dashboard.md](../guidelines/dashboard.md); this file is how to decide.

## Contents
- Principles
- The Style Profile (fields and values)
- Deriving a profile (order of precedence)
- Goal bases
- Audience overrides
- Data-character modifiers
- Color system
- Typography scale
- Chart vocabulary
- Anomaly treatment
- Narrative and annotation weight
- Worked examples

## Principles

1. **One thing first.** Every page has a single primary surface: the number, chart, or sentence the reader must see before anything else. If you can't name it, the layout isn't done.
2. **Neutral by default, color is a sentence.** Ink is grey unless color says something: *this is the subject*, *this broke a limit*, or *this is category X*. Anything else is decoration and is removed.
3. **Titles state, axes inform.** A title is a finding with its number ("Returns peaked at 10.3% in November"). Axis labels carry units. "Revenue by month" is never a title.
4. **Density is earned by interaction.** A dense page is only allowed when the reader can reduce it (filters, brushing, a detail table). A page nobody can filter must be sparse.
5. **Exact beats smooth in formal registers.** Where numbers are reconciled or audited, no curve interpolation, no rounding that hides a threshold crossing, no truncated axes on bars.
6. **Anomalies are explained or flagged, never smoothed away.** An outlier is either the story (spotlight it), noise you've ruled out (footnote it), or unknown (flag it). It's never silently averaged into a trend.
7. **Trust scales with the audience.** The more formal the reader, the more visible the provenance: from hidden (me), to footnoted (leadership), to a definition and source beside every number (regulators).
8. **Motion explains change and order.** Animate a transition the reader caused (a filter), a change worth seeing (before/after, play through time), or the reading order as the page opens (`reveal`). Never decoration, never a tween that shows values the data doesn't have, never for regulators. Patterns: [motion.md](motion.md).
9. **The executor doesn't improvise.** Everything the page needs to look right is in the profile. If something is missing, the executor asks the planner; it doesn't fill the gap with defaults.

## The Style Profile

Written as bullets in the plan's `## Style` section (`- field: value`). Every field is required unless marked optional.

| Field | Values | What it controls |
|---|---|---|
| `register` | `analytic`, `operational`, `editorial`, `formal`, `evidentiary` | overall voice: how declarative, how much provenance |
| `density` | `sparse`, `balanced`, `dense` | number of blocks and charts on the first screen (caps below) |
| `surface` | `headline`, `status`, `grid`, `narrative`, `ledger`, `exact`, `stage` | the primary surface: what sits at the top and takes the most space; `stage` is a one-screen page that morphs through scenes ([stage.md](stage.md)) |
| `focus` | free text, one phrase | what the focus color marks, e.g. `the driver category`, `off-target stores`, `selected series` |
| `color_mode` | `focus`, `status`, `categorical`, `sequential`, `diverging` | how color is used on the page (see Color system) |
| `direction` | `up-good`, `down-good`, `none` | whether increases are good; required for status and diverging color |
| `type_scale` | `compact`, `standard`, `display` | size steps for KPIs, titles, body (see Typography) |
| `interaction` | `none`, `light`, `full` | how many controls the page has (see table below) |
| `motion` | `none`, `transitions`, `reveal` | allowed animation |
| `chart_set` | comma list of plan forms | the only forms the page may use |
| `anomalies` | `ignore`, `flag`, `spotlight`, `explain`, `footnote` | how outliers and breaks are treated |
| `narrative` | `none`, `captions`, `annotated`, `story` | how much prose and annotation |
| `provenance` | `hidden`, `footnote`, `inline`, `per-number` | how visible sources and definitions are |
| `numbers` | `rounded`, `precise`, `exact` | precision of displayed values |
| `data_character` | comma list (see modifiers) | the traits detected in the data; recorded for traceability |
| `accent`, `alert`, `currency` | `#hex`, `#hex`, ISO code (optional) | the suggested `focus` and `breach` colors for this page (see Color system), or the brand colors pinned in `guidelines/dashboard.md` |

### Density caps (first screen)

| density | KPI tiles | charts | menus | detail table |
|---|---|---|---|---|
| `sparse` | ≤ 4 | ≤ 3 | ≤ 1 | no |
| `balanced` | ≤ 5 | ≤ 6 | ≤ 3 | collapsed |
| `dense` | ≤ 8 | ≤ 12 (small multiples count as one) | any | yes |

### Interaction levels

| interaction | brush | click filter | menus | hover tooltips | Reset + chips | detail table |
|---|---|---|---|---|---|---|
| `none` | no | no | no | yes | no | no |
| `light` | 1 chart | 1 chart | ≤ 1 | yes | yes | no |
| `full` | every time/number chart | every categorical chart | every useful dimension | yes | yes | yes |

## Deriving a profile

Apply in this order; a later layer overrides an earlier one only where stated:

1. **Goal base** sets every field.
1b. **Page format** from the intake (`format`) replaces the goal base's `surface` (Page format table in `guidelines/goals.md`); the rest of the base stays.
2. **Audience overrides** apply next. They are **hard constraints**: nothing after them may loosen them.
3. **Data-character modifiers** adjust what the audience still allows (they can tighten, add, or swap within the allowed set; they never loosen an audience constraint).
4. **Two goals:** take the base of the first goal; from the second goal take only `narrative` (if heavier) and its blocks (and, for `impact`, its `type_scale` and `motion`). Monitor always contributes its status row on top; present always contributes its story at the bottom.
5. **Spec goal:** the person's request wins over the base for layout and chart forms; audience overrides still apply to provenance, numbers and SQL.

Record the result in the plan, then check it against any stricter limits in `guidelines/dashboard.md`. `scripts/validate_plan.py` enforces the hard constraints.

## Goal bases

| Field | answer | explore | monitor | present | spec | impact |
|---|---|---|---|---|---|---|
| register | analytic | analytic | operational | editorial | analytic | editorial |
| density | balanced | dense | sparse | sparse | as asked | balanced |
| surface | headline | grid | status | narrative | exact | headline |
| color_mode | focus | categorical | status | focus | focus | categorical |
| type_scale | standard | compact | standard | display | standard | display |
| interaction | light | full | light | none | as asked | light |
| motion | transitions | reveal | none | reveal | none | reveal |
| chart_set | bar, trend, KPIs | bar, trend, histogram, scatter | KPIs, exceptions, trend | bar, trend, KPIs | as asked | KPIs, bar, trend, histogram, scatter |
| anomalies | explain | flag | spotlight | explain | flag | spotlight |
| narrative | captions | none | none | story | none | annotated |
| provenance | footnote | hidden | footnote | footnote | footnote | footnote |
| numbers | rounded | precise | precise | rounded | precise | rounded |

What each base means in practice:
- **answer:** a headline sentence with the answer and its number on top; the driver chart before the trend; the focus color marks only the driver.
- **explore:** a grid of linked small charts with consistent category colors across every chart; no prose; the reader does the work.
- **monitor:** a status row first (on/off target per KPI), then the exceptions list; color appears only where something is off target; a last-updated stamp is mandatory.
- **present:** one finding per section, top to bottom; each chart has one annotated moment and a sentence that says why it matters; large type; little or no interaction.
- **spec:** draw exactly what was asked; style decides only how, never what.
- **impact:** the page has to earn a second look. One animated hero (the brief's hook) fills the first screen; every chart under it is an unconventional form from `visual-language.md` with its own motion (`motion.md`); KPIs count up and carry their trajectory. Impact never buys a broken honesty rule.

As a second goal, `impact` contributes its `type_scale`, `motion` and `narrative` when heavier, and its rule that no chart uses the conventional form.

## Audience overrides

Hard constraints. The organization can tighten these in `guidelines/dashboard.md`, never loosen them.

| Field | me | team | leadership | clients | regulators |
|---|---|---|---|---|---|
| KPI tiles (max) | 8 | 6 | 5 | 4 | 4 |
| SQL on page | yes | yes | no | no | no |
| density (max) | dense | dense | balanced | balanced | balanced |
| interaction (max) | full | full | light | light | light |
| motion (max) | reveal | reveal | reveal | reveal | none |
| register | (goal) | (goal) | declarative: analytic→editorial | formal | evidentiary |
| type_scale (min) | compact | compact | standard | standard | standard |
| labels | column names OK | short names | plain language only | plain language, no jargon | defined terms only, each with its definition |
| provenance (min) | hidden | hidden | footnote | footnote | per-number |
| numbers | (goal) | (goal) | rounded | rounded | exact |
| anomalies | (goal) | (goal) | explain or spotlight | explain | footnote (with the reconciling figure), never spotlight |
| chart_set (remove) | none | none | scatter, histogram unless it is the answer | scatter, histogram | scatter, any smoothed curve, stacked area, dual axis |
| narrative (min) | none | none | captions | captions | captions (definitions, not persuasion) |
| reconcile | (request) | (request) | (request) | (request) | always on |

Notes:
- **leadership:** declarative titles, one number per sentence, nothing to decode. If a chart needs a legend to be read, replace it with direct labels.
- **clients:** polished and restrained: no internal codes, no raw ids, no "TBD", consistent number formats on every tile.
- **regulators:** every key number shows its definition and source next to it; lines are drawn point to point (no smoothing); percentages near a threshold show enough decimals that the side of the threshold is unambiguous; no animation; a visible as-of date.

## Data-character modifiers

Detect these from the profile (`1-profile/profile.txt` and `quick-look.json`). Record the ones that apply in `data_character`.

| Trait | Detected when | Effect (within what the audience allows) |
|---|---|---|
| `time-heavy` | a date column covering ≥ 8 buckets at the suggested grain | trend is the primary chart for answer/monitor; add `comparison_period`; brush on the trend |
| `categorical` | ≥ 2 dimensions with 3–30 values | ranked bars, sorted by value; categorical color only when categories repeat across charts, else focus |
| `high-cardinality` | a dimension with > 30 values | never color by it; top 10 + "Other" in bars; offer it as a menu or search, not a chart axis |
| `anomaly-rich` | max > 10× p99 on a measure, or a time bucket > 3 MAD from the median | `anomalies` at least `flag`; spotlight only if the anomaly is the answer; never let it set an axis alone (cap the axis and mark the clipped value) |
| `sparse` | > 15% nulls in a used column, or > 10% missing time buckets | show gaps as gaps (no interpolation); add a coverage note; `numbers` no finer than the data supports |
| `small-n` | < 200 rows, or a category with < 30 rows | show counts beside rates; no percentages without the denominator; prefer dots/strips over histograms |
| `ordinal` | a measure with ≤ 11 small-integer values (ratings) | averages or distributions, never sums; diverging color around the scale midpoint |
| `wide` | > 6 measures | small multiples on a shared scale instead of many separate charts; density at least `balanced` if allowed |
| `flag-driven` | a yes/no column used as a rate | the rate is a KPI; status color only if a target exists |

## Color system

Colors are **roles**, not fixed hex values. For each dashboard, suggest a value for every role the page's `color_mode` allows, in light and dark mode, following the rules below and in `guidelines/dashboard.md` (which may pin brand colors instead). Put the suggestion on the confirmation card as an assumption ("Colors: blue focus, orange-red for off target") so the person can change it, then write `focus` as `accent` and `breach` as `alert` in the plan.

| Role | Meaning | Rule |
|---|---|---|
| `ink` | text, axes, the default mark | most of the page; every series starts here |
| `ink-muted` | context: other series, past periods, gridlines | ≥ 70% of colored area should be ink or ink-muted |
| `focus` | the subject named in the profile's `focus` | at most one focus hue per chart, at most two items in focus per page |
| `selected` | what the reader clicked or brushed | never the same as `focus` |
| `good`, `bad` | movement in the declared `direction` | only when `direction` is set; always paired with a sign or arrow (never color alone) |
| `breach` | a value past its target or limit | only on the breaching element, never on the whole chart |
| `category-1…6` | categorical series | max 6; the 7th and beyond become "Other" in `ink-muted`; the same category keeps the same color on every chart |
| `sequential` | magnitude on one scale | one hue from light to dark; only for ordered values |
| `diverging` | above vs below a declared midpoint | only when the midpoint means something (target, zero, scale middle); state it on the legend |

`color_mode` picks which roles may appear:

| color_mode | Roles allowed |
|---|---|
| `focus` | ink, ink-muted, focus, selected |
| `status` | ink, ink-muted, breach, good/bad (with direction), selected |
| `categorical` | ink, ink-muted, category-1…6, selected |
| `sequential` | ink, ink-muted, sequential, selected |
| `diverging` | ink, ink-muted, diverging, selected |

## Typography scale

All numbers use tabular figures. Units live in labels, not in every value.

| type_scale | body | chart title | KPI value | page title | line height |
|---|---|---|---|---|---|
| `compact` | 12–13 px | 13 px medium | 22–24 px | 20 px | 1.4 |
| `standard` | 14 px | 15 px medium | 30–32 px | 24 px | 1.5 |
| `display` | 16 px | 18 px medium | 44–56 px | 32 px | 1.6 |

- `register: editorial` or `display` scale: the headline finding may use a serif for the title and the hero number; everything else stays sans.
- `register: formal` or `evidentiary`: one family only, no display serif, no all-caps labels.

## Chart vocabulary

The plan may only use forms in `chart_set`. How each form is *drawn* is chosen with [visual-language.md](visual-language.md): the conventional form is known and set aside, and its honesty rules always hold. Beyond the audience removals above:
- **Never:** pie or donut with > 5 slices, decorative 3D (3D bars, pies, extruded single measures), dual axes, radar, gauges, word clouds. 3D is allowed only when all three axes are data ([stage.md](stage.md) §5).
- **Bars** start at zero, sorted by value unless the categories have an order.
- **Lines** are drawn point to point; smoothing only for `register: editorial` and never on a line a number is read from.
- **Histograms** only when the spread is the point; otherwise a box or strip.
- **Scatter** only with ≥ 30 points and a stated question about the relationship.
- **Small multiples** before stacked charts when there are > 3 series.

## Anomaly treatment

| anomalies | On the page |
|---|---|
| `ignore` | nothing; only valid when the profile found no anomaly |
| `flag` | a small marker on the point plus a tooltip with the value and how unusual it is |
| `spotlight` | focus color on the anomaly, annotation with its number, other marks muted |
| `explain` | annotation with the number **and** the cause if known ("Black Friday", "data outage"); "cause unknown" if not |
| `footnote` | marker plus a numbered footnote with the value, the expected range, and the reconciling figure |

Axis rule for every mode: one extreme value must not compress the rest. Cap the axis and mark the clipped value with its true number.

## Narrative and annotation weight

| narrative | Prose | Annotations | Titles |
|---|---|---|---|
| `none` | none | anomalies only | neutral labels allowed |
| `captions` | one sentence under the page title | ≤ 1 per chart | findings |
| `annotated` | one sentence per chart | 1–2 per chart at the key moments | findings |
| `story` | a short paragraph per section, written to be read in order | the key moment of every chart | findings, phrased as the section's claim |

## Worked examples

**Monthly return-rate review for leadership** (goal answer + present, audience leadership, data time-heavy + categorical + flag-driven):

```
- register: editorial
- density: balanced
- surface: headline
- focus: the store driving the rise
- color_mode: focus
- direction: down-good
- type_scale: display
- interaction: light
- motion: transitions
- chart_set: KPIs, bar, trend
- anomalies: explain
- narrative: story
- provenance: footnote
- numbers: rounded
- data_character: time-heavy, categorical, flag-driven
```

**Daily breach check for auditors** (goal monitor, audience regulators, data time-heavy + sparse):

```
- register: evidentiary
- density: sparse
- surface: status
- focus: accounts past the limit
- color_mode: status
- direction: down-good
- type_scale: standard
- interaction: light
- motion: none
- chart_set: KPIs, exceptions, trend
- anomalies: footnote
- narrative: captions
- provenance: per-number
- numbers: exact
- data_character: time-heavy, sparse
```

**Analyst exploring support tickets for themselves** (goal explore, audience me, data categorical + high-cardinality + ordinal):

```
- register: analytic
- density: dense
- surface: grid
- focus: selected series
- color_mode: categorical
- direction: none
- type_scale: compact
- interaction: full
- motion: transitions
- chart_set: bar, trend, histogram, scatter
- anomalies: flag
- narrative: none
- provenance: hidden
- numbers: precise
- data_character: categorical, high-cardinality, ordinal
```
