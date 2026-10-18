# Motion with D3

Motion is what makes a page feel alive, and it is also the easiest way to lie (a scale that jumps, a tween that overshoots). Use it to show *change* and *order*: what changed when the reader filtered, what to read first when the page opens, how something evolved when time plays. The rules that keep it honest are Part 3 rules 17–19 of [visual-language.md](visual-language.md).

The Style Profile's `motion` sets the ceiling: `none` (end states only), `transitions` (marks move when the filter changes), `reveal` (transitions, plus staged entrance, count-ups and a time player).

## Contents
- Setup
- 1. A D3 chart as a Mosaic client, with transitions
- 2. Clicks and brushes from a D3 chart
- 3. Reveal: staged entrance in reading order
- 4. Count-up numbers
- 5. Play through time
- 6. Morph between views
- Timing and easing
- Pitfalls

## Setup

```js
import * as vg from "https://cdn.jsdelivr.net/npm/@uwdata/vgplot@0.31.0/+esm";
import { clausePoints, clauseInterval } from "https://cdn.jsdelivr.net/npm/@uwdata/mosaic-core@0.31.0/+esm";
import * as d3 from "https://cdn.jsdelivr.net/npm/d3@7.9.0/+esm";

// The system's reduced-motion setting is the default; the viewer can override it with the page's Motion switch.
const SYSTEM_REDUCED = matchMedia("(prefers-reduced-motion: reduce)").matches;
let saved = null; try { saved = localStorage.getItem("motion"); } catch {}
let REDUCED = saved ? saved === "off" : SYSTEM_REDUCED;
const T = (ms) => (REDUCED ? 0 : ms);          // every duration goes through T()
let quick = false, quickTimer;                  // true while a brush is dragged or the player runs
const hurry = () => { quick = true; clearTimeout(quickTimer); quickTimer = setTimeout(() => (quick = false), 400); };
const dur = () => T(quick ? 160 : 500);         // update transitions: short under the hand, smooth otherwise
```

### The Motion switch

Many machines have reduced motion on (Windows: Settings › Accessibility › Visual effects › Animation effects off), and then a page that honors it shows no animation at all, which looks broken to someone who expects it. Every page with `motion` above `none` has a small switch in its filter bar: "Motion: on/off", starting from the system setting, remembered in the browser. When the system asks for reduced motion and the switch is off, show a one-line hint beside it ("Animations are off: your system asks for reduced motion").

```js
const motionBtn = document.getElementById("motion");
const label = () => { motionBtn.textContent = REDUCED ? "Motion: off" : "Motion: on"; motionBtn.setAttribute("aria-pressed", String(!REDUCED)); };
motionBtn.addEventListener("click", () => {
  REDUCED = !REDUCED; try { localStorage.setItem("motion", REDUCED ? "off" : "on"); } catch {}
  label(); location.reload();                                // replay the page with the new setting
});
label();
```

CSS that animates (`.reveal`) keys off a class on `<html>` the script sets (`motion-on`), not only the media query, so the switch controls CSS motion too.

## 1. A D3 chart as a Mosaic client, with transitions

The client asks DuckDB for exactly what it draws and redraws whenever the page filter changes. Keyed joins (`data(rows, key)`) let each mark move from its old value to its new one instead of being redrawn.

```js
class D3Client extends vg.MosaicClient {
  constructor(filterBy, query, draw) { super(filterBy); this.q = query; this.draw = draw; }
  query(where = []) { return this.q(where); }
  queryResult(data) { this.draw(data.toArray().map((d) => ({ ...d }))); return this; }
  queryError(e) { console.error(e); return this; }
}

// Example: ranked bars that slide into their new order and length on every filter.
const svg = d3.select("#rank").append("svg").attr("viewBox", [0, 0, W, H]);
const x = d3.scaleLinear().range([M.left, W - M.right]);
const y = d3.scaleBand().range([M.top, H - M.bottom]).padding(0.25);
const axis = svg.append("g").attr("transform", `translate(0,${H - M.bottom})`);
const draw = (rows) => {
  x.domain([0, d3.max(rows, (d) => d.v) || 1]);          // zero baseline: rule 1
  y.domain(rows.map((d) => d.k));
  const t = svg.transition().duration(T(450)).ease(d3.easeCubicOut);
  svg.selectAll("rect").data(rows, (d) => d.k).join(
    (enter) => enter.append("rect").attr("x", x(0)).attr("y", (d) => y(d.k)).attr("height", y.bandwidth()).attr("width", 0),
    (update) => update,
    (exit) => exit.transition(t).attr("width", 0).remove(),
  ).transition(t).attr("y", (d) => y(d.k)).attr("height", y.bandwidth()).attr("width", (d) => x(d.v) - x(0));
  axis.transition(t).call(d3.axisBottom(x).ticks(4, "~s"));   // the axis moves with the marks: rule 17
};
const q = (where) => vg.Query.from("t").select({ k: "category", v: vg.sum("amount") }).where(where).groupby("category").orderby(vg.desc("v"));
vg.coordinator().connect(new D3Client($page, q, draw));
```

## 2. Clicks and brushes from a D3 chart

A D3 chart filters the page through its **own** selection relayed into the page filter (see `mosaic-tech.md`), and passes itself as the clause source so it isn't filtered by its own click.

```js
const $mine = vg.Selection.single(); $mine._relay.add($page);
const client = new D3Client($page, q, draw);
const src = { source: client, clients: new Set([client]) };
let picked = [];
rects.on("click", (event, d) => {
  picked = event.shiftKey ? [...new Set([...picked, d.k])] : (picked.length === 1 && picked[0] === d.k ? [] : [d.k]);
  $mine.update(clausePoints(["category"], picked.length ? picked.map((k) => [k]) : null, src));
  svg.selectAll("rect").transition().duration(T(200)).attr("opacity", (r) => (!picked.length || picked.includes(r.k) ? 1 : 0.3));
});
// A brush: d3.brushX().on("brush end", ({ selection }) =>
//   $mine.update(clauseInterval("date", selection ? selection.map(x.invert) : null, src)));
```

Use `"brush end"` (not only `"end"`) so the page updates while dragging.

## 3. Reveal: staged entrance in reading order

Only with `motion: reveal`. Each section fades and rises once, when it first scrolls into view, in the order the story is read. Charts draw from their baseline (bars grow from zero, lines draw left to right), so the entrance itself says how to read the chart.

```css
.reveal { opacity: 0; transform: translateY(12px); transition: opacity .6s ease, transform .6s ease; }
.reveal.in { opacity: 1; transform: none; }
@media (prefers-reduced-motion: reduce) { .reveal { opacity: 1; transform: none; transition: none; } }
```

```js
const io = new IntersectionObserver((entries) => entries.forEach((e) => {
  if (e.isIntersecting) { e.target.classList.add("in"); io.unobserve(e.target); }
}), { threshold: 0.15 });
document.querySelectorAll(".reveal").forEach((el) => io.observe(el));

// A line that draws itself left to right, once:
path.attr("stroke-dasharray", function () { return this.getTotalLength(); })
    .attr("stroke-dashoffset", function () { return this.getTotalLength(); })
    .transition().duration(T(1200)).ease(d3.easeCubicInOut).attr("stroke-dashoffset", 0)
    .on("end", function () { d3.select(this).attr("stroke-dasharray", null); });  // later updates redraw normally
```

## 4. Count-up numbers

A KPI that tweens from its previous value to its new one. Interpolate real values only (no overshoot easing: rule 18).

```js
function tweenNumber(el, to, format) {
  const from = el.__v ?? 0; el.__v = to;
  d3.select(el).transition().duration(T(700)).ease(d3.easeCubicOut)
    .tween("text", () => { const i = d3.interpolateNumber(from, to); return (t) => { el.textContent = format(i(t)); }; });
}
```

## 5. Play through time

Play is an **animated brush**: a timer moves the time chart's own D3 brush across the period, gliding (below). The window is the same selection a hand-drawn brush makes, so the chips, Reset and every chart treat it the same way, and the reader sees the window travel across the time chart.

```js
const brush = d3.brushX().extent([[M.left, M.top], [W - M.right, H - M.bottom]])
  .on("brush end", ({ selection, sourceEvent }) => {
    if (sourceEvent) hurry();                                  // a hand drag: short transitions (Timing)
    $dates.update(clauseInterval("date", selection ? selection.map((px) => x.invert(px)) : null, src));
  });
const gb = svg.append("g").call(brush);
const move = (range) => gb.call(brush.move, range ? range.map(x) : null);   // dates in, pixels out
```

### Glide: Play without stutter

A Play that jumps a week every half second, with short transitions in between, stops and starts: that reads as stutter. Make it glide:

1. **The window moves every frame** (`d3.timer`), at a steady speed in days per second, so the brush itself never jumps.
2. **The filter updates as fast as DuckDB answers, never faster:** send a new clause only when the previous query has returned (a `busy` flag cleared in `queryResult`), at most every ~120 ms.
3. **Every chart's update transition lasts as long as one update cycle and uses `d3.easeLinear`,** so each transition is still running when the next data arrives; interrupting it continues from where the mark is, and the motion is continuous.

```js
let playing = false, busy = false, lastSent = 0, speed = 9;   // days per second (≈ 40 s for a year)
const glideDur = () => (playing ? 260 : null);                 // charts: duration = glideDur() ?? dur(), ease = linear while playing
function play() {
  playing = true; let lo = START; const width = 28 * DAY; const t0 = performance.now();
  const timer = d3.timer(() => {
    lo = START + ((performance.now() - t0) / 1000) * speed * DAY;
    if (lo + width > END) { timer.stop(); playing = false; return; }
    moveBrushVisualOnly([lo, lo + width]);                     // brush.move inside a flag the brush handler ignores
    const now = performance.now();
    if (!busy && now - lastSent > 120) { busy = true; lastSent = now; $dates.update(clauseInterval("date", [new Date(lo), new Date(lo + width)], src)); }
  });
}
// Clear busy in the queryResult of a client that follows every filter (the KPI numbers, say): views that ignore the
// time filter never re-query during Play, so a busy flag waiting on them would stop the filter updating.
// In each client's queryResult, draw with
//   sel.transition().duration(glideDur() ?? dur()).ease(playing ? d3.easeLinear : d3.easeCubicOut)
```

A hand-drawn brush uses the same rules while it is dragged.

### The hero keeps its context

A chart whose story is the whole period (a bump chart of rank over the year) collapses if a 4-week window filters it. Let it follow only the menus, and show the time filter as a highlighted band over the period it covers and a family filter as emphasis. Say so in the technical notes. Every other chart follows the full page filter.

## 6. Morph between views

For chains through many forms (a show reel), use the polygon engine in [show-reel.md](show-reel.md); the patterns below are its simplest cases.

The most memorable D3 motion is a chart turning into another chart: the same marks fly from one encoding to another, so the reader sees that both views are the same data. Use it when two honest views of one dataset each answer a different question (rank vs. share, units vs. totals, a cycle vs. a line, a calendar vs. a timeline). Give the card a small view switch ("Rank · Share") and morph on click; with `impact`, at least one chart on the page morphs.

Rules: both views must be true on their own (each passes `visual-language.md` Part 3), the marks keep their identity (same key, same color) through the morph, and axes and labels fade out and back in with the new view, never left showing the old scale.

**Unit morph:** each datum is one mark with a layout per view; the transition moves it.

```js
// Each view returns the mark's geometry for a datum: computed from the data, never typed in.
const views = {
  grid: (d) => ({ x: (d.i % cols) * step, y: Math.floor(d.i / cols) * step, w: size, h: size, rx: 3 }),
  bars: (d) => ({ x: x0 + d.k * unit, y: band(d.category), w: unit - 1, h: band.bandwidth(), rx: 1 }),
};
function morphTo(name) {
  const at = views[name];
  marks.transition().duration(T(900)).delay((d) => T(d.i * 6)).ease(d3.easeCubicInOut)
    .attr("x", (d) => at(d).x).attr("y", (d) => at(d).y).attr("width", (d) => at(d).w).attr("height", (d) => at(d).h).attr("rx", (d) => at(d).rx);
  guides.selectAll("[data-view]").transition().duration(T(300)).attr("opacity", function () { return this.dataset.view === name ? 1 : 0; });
}
```

**Shape morph:** for marks whose outline changes (a radial bar unrolling into a straight bar, a slice into a bar), describe both outlines with the **same number of points in the same order** and interpolate the points. No extra library needed.

```js
const K = 16;                                                     // points per edge
const radialBar = (d) => {                                         // outer edge clockwise, inner edge back
  const a = d3.range(K).map((j) => a0(d) + (a1(d) - a0(d)) * j / (K - 1));
  return [...a.map((t) => [Math.sin(t) * rOut(d), -Math.cos(t) * rOut(d)]), ...a.reverse().map((t) => [Math.sin(t) * rIn, -Math.cos(t) * rIn])];
};
const straightBar = (d) => {                                       // top edge left→right, bottom edge back
  const xs = d3.range(K).map((j) => left(d) + width(d) * j / (K - 1));
  return [...xs.map((x) => [x, top(d)]), ...xs.reverse().map((x) => [x, bottom])];
};
const toPath = (pts) => "M" + pts.map((p) => p.join(",")).join("L") + "Z";
paths.transition().duration(T(1100)).ease(d3.easeCubicInOut)
  .attrTween("d", function (d) { const i = d3.interpolateArray(this.__pts ?? radialBar(d), straightBar(d)); this.__pts = straightBar(d); return (t) => toPath(i(t)); });
```

Draw both views from the same polygon function from the start (not `d3.arc` for one and `rect` for the other), so every morph starts from the outline on screen. Keep the current view in a variable, so a filter redraw uses the view the reader picked.

**Staging, like D3's own demos:** split a big morph into two or three steps chained with `.transition()`: first move the marks into place, then resize them, then bring in the new axis. Each step 400–700 ms. A reader follows two short moves better than one long one.

## Timing and easing

| Change | Duration | Easing |
|---|---|---|
| Filter while brushing | 120–200 ms (or none) | `easeLinear` |
| Filter on click / menu | 350–500 ms | `easeCubicOut` |
| Entrance (reveal) | 600–1200 ms, staggered 60–100 ms per item | `easeCubicOut` / `easeCubicInOut` |
| Count-up | 500–800 ms | `easeCubicOut` |
| Morph between views | 900–1200 ms in 2–3 staged steps | `easeCubicInOut` |
| Play (glide) | window moves every frame; updates every ≥ 120 ms when the last query is back; update transitions ≈ 260 ms | `easeLinear` while playing |

Never `easeBack`, `easeElastic` or `easeBounce` on a value: they show numbers the data doesn't have.

## Pitfalls

- **Start after the first data.** Connect every client, wait until each has delivered its first result, then run the opening scene and the count-ups. Entrances that start while the initial results are still arriving stall partway: a bar frozen as a hairline, numbers that crawl for half a minute.

- **Nothing typed in.** Categories, their order and colors, the date span, the busiest or slowest point, an outage: all come from queries on the data, so the page stays true when the data changes or a filter applies. The plan supplies titles and captions; the page's code supplies no numbers or category names of its own.

- **Reset doesn't move a D3 brush.** `selection.reset()` clears the clause but leaves the brush drawn; call `brush.move(null)` (or `move(null)` above) first.
- **Short transitions while dragging.** Keep a `quick` flag that a brush drag or the player sets for ~400 ms, and use `T(quick ? 160 : 500)` for update durations; long transitions lag behind the hand.
- **Zoomed time axes repeat labels.** Month-formatted ticks on a 3-month window print "Aug Aug Aug"; switch to day-level ticks (`"%b %-d"`) when the domain is under ~150 days.
- **Phones:** a 1,000-unit-wide `viewBox` shrinks text to ~4 px at 375 px. Give wide charts a `min-width` (≈ 640–760 px) inside an `overflow-x: auto` wrapper, so the chart scrolls inside its card and the page never does.
- **Labels from the data in view.** Annotations that name a value ("Fastest 1.1 s, week of Sep 22") should be computed in `draw()` from the rows shown, so they stay true under every filter; fixed annotations go only where the date is fixed (an outage).

- **Transitions pile up while brushing.** A new transition on the same element interrupts the previous one (same name), which is what you want; don't give update transitions unique names.
- **`.join()` with a transition:** call `.transition()` on the joined selection, not inside `update`, or entering marks skip the animation.
- **Draw-on lines:** remove `stroke-dasharray` when the entrance ends, or later updates with a different path length look cut off.
- **Width:** size with `viewBox` and `width: 100%`; a hidden tab reports 0 width (see `mosaic-tech.md`).
- **Arrow values:** wrap rows with `{ ...row }`; BigInt sums need `Number()` before D3 scales.
- **Dates from DuckDB** arrive as epoch ms; wrap with `new Date(v)`.
