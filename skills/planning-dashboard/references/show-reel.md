# Show reel: one set of marks, many charts

D3's Show Reel takes one dataset through lines, areas, stacks, streams, bars and a pie without ever redrawing from scratch: every mark visibly travels from one chart into the next. This file is how to do that here, for any data, with every form honest.

The design seed (`scripts/design_seed.py`) picks the chains of forms for a run. Build them from an empty file each time: never open or copy a previous dashboard's page.

## Contents
- 1. Mark units
- 2. The polygon engine
- 3. Form catalog
- 4. Moving between forms
- 5. 3D in SVG with d3-3d
- 6. Icons
- 7. Checks

## 1. Mark units

A mark unit is what one mark stands for. A chain stays on one unit, so marks keep their identity from form to form.

| Unit | id | Example marks |
|---|---|---|
| category × period | `cp` | one mark per model and month, store and week |
| period | `p` | one mark per day |
| cycle position | `c` | one mark per hour of day, weekday |
| category | `k` | one mark per category, or per 1% of the total |
| period × cycle | `g` | one mark per day and hour |

Pass the units the data supports to `design_seed.py --units`, main story first.

## 2. The polygon engine

Every mark is drawn as **three polygons with the same number of points K in every form**: `front`, `top` and `side`. In 2D forms `top` and `side` collapse onto an edge of `front` (zero area); in 3D forms they are the projected faces of a box. Because every form produces the same structure, *any* form can morph into *any* other by interpolating points, including 2D into 3D.

```js
const K = 24;                                                    // points per polygon, the same everywhere
const lerp = (a, b, t) => a + (b - a) * t;
// Resample any closed outline (corner list) to K points, starting at its top-left corner, clockwise.
function resample(corners) {
  const segs = corners.map((p, i) => [p, corners[(i + 1) % corners.length]]);
  const lens = segs.map(([a, b]) => Math.hypot(b[0] - a[0], b[1] - a[1])), total = d3.sum(lens) || 1;
  const out = [];
  for (let i = 0; i < K; i++) {
    let d = (i / K) * total, s = 0;
    while (s < segs.length - 1 && d > lens[s]) d -= lens[s++];
    const [a, b] = segs[s], t = lens[s] ? d / lens[s] : 0;
    out.push([lerp(a[0], b[0], t), lerp(a[1], b[1], t)]);
  }
  return out;
}
const rect = (x, y, w, h) => resample([[x, y], [x + w, y], [x + w, y + h], [x, y + h]]);
const circle = (cx, cy, r) => d3.range(K).map((i) => { const a = -Math.PI * 3 / 4 + (i / K) * 2 * Math.PI; return [cx + r * Math.cos(a), cy + r * Math.sin(a)]; });
const wedge = (cx, cy, r0, r1, a0, a1) => {                        // a radial bar or slice; angles clockwise from 12 o'clock
  const n = K / 2, arc = (r, from, to) => d3.range(n).map((j) => { const a = lerp(from, to, j / (n - 1)); return [cx + r * Math.sin(a), cy - r * Math.cos(a)]; });
  return [...arc(r1, a0, a1), ...arc(r0, a1, a0)];
};
const flat = (poly) => poly.map(([x, y]) => [x, y]);              // a collapsed top/side: same points as an edge
const edgeTop = (p) => { const xs = d3.extent(p, (q) => q[0]), y = d3.min(p, (q) => q[1]); return resample([[xs[0], y], [xs[1], y], [xs[1], y], [xs[0], y]]); };
const toPath = (p) => "M" + p.map((q) => q[0].toFixed(1) + "," + q[1].toFixed(1)).join("L") + "Z";
```

Each form is a function `layout(mark) → { front, top, side, fill, opacity }`. A 2D form returns `top: edgeTop(front)` and `side: edgeTop(front)` so the extra faces sit invisibly on the mark's top edge, ready to grow.

```js
function morph(form, ms, enter) {
  marks.each(function (d) {
    const g = d3.select(this), next = form(d);
    for (const face of ["side", "top", "front"]) {
      const path = g.select("." + face), to = next[face];
      if (!path.node().__pts) {                                    // a new mark: draw its start shape now, or it flashes in from (0,0)
        path.node().__pts = enter ? enter(next)[face] : to;        // enter(next) = the collapsed shape it grows from, e.g. its baseline edge
        path.attr("d", toPath(path.node().__pts));
      }
      path.transition().duration(ms).delay(stagger(d)).ease(EASE)
        .attrTween("d", function () {                              // runs when the transition starts, so it reads what is on screen
          const i = d3.interpolateArray(this.__pts, to);
          return (t) => toPath((this.__pts = i(t)));               // keep the current points: an interrupted morph continues from here
        })
        .attr("fill", shade(next.fill, face)).attr("opacity", next.opacity);
    }
  });
}
```

Keep the points that are on screen, not the last target: a filter or a scene click that lands mid-morph otherwise makes every mark jump to where the previous morph was going before it moves on.

**Point order matters as much as point count.** Interpolation pairs point *j* with point *j*, so every outline must start at the same place and run the same way (here: top-left, clockwise). Perimeter resampling also puts a different number of points on each edge when the aspect ratio changes (a tall bar into a wide band), so corners drift round the outline and marks twist mid-morph. For marks that have a top and a bottom edge (bars, slices, bands, boxes' faces, even circles as two half-arcs), sampling both edges at the same K/2 positions, top left→right then bottom right→left, keeps every point on its own edge through any morph.

## 3. Form catalog

Layouts for the forms `design_seed.py` suggests. They are starting points: an invented form joins a reel the same way, as long as it produces the three polygons per mark (§2). All are honest by construction: lengths and areas from zero, areas proportional to values, one measure per axis. The `~ draw:` line in the plan names each scene's form.

| Unit | Form | Mark geometry (front polygon) |
|---|---|---|
| cp | `stacked-area` | slice between the stacked lines at the period's left and right edges (4 corners: x0,y0top → x1,y1top → x1,y1base → x0,y0base) |
| cp | `stacked-100` | same slice, values divided by the period total |
| cp | `stream` | slices around a centre baseline (`d3.stackOffsetWiggle`): shape only, never read values off it (label it so) |
| cp | `stacked-bars` / `stacked-bars-100` | a rect per period column, stacked by category |
| cp | `grouped-bars` | rects side by side within each period's band |
| cp | `small-multiple-bars` / `-lines` | one panel per category (shared y), a rect per period, or a thin slice along the line |
| cp | `lines` / `bump` | a short thick segment from the period's point to the next (rank for bump) |
| cp | `dots` | a circle at (period, value) |
| cp | `heat-cells` | a rect in a category × period grid, colored by value (sequential, legend) |
| cp | `3d-bars` | a box at (period, category) with height = value (§5) |
| cp | `treemap` | a rect from `d3.treemap` of category → period (area = value) |
| p | `strip`, `beeswarm`, `unit-histogram` | circles on a time axis; dodged by value; stacked in value bins |
| p | `timeline-bars`, `calendar`, `spiral`, `horizon` | rects on time; week × weekday grid; positions on an Archimedean spiral (one turn per week or month); horizon bands |
| c | `bars`, `dot-plot`, `radial-bars` | rects; circles on a value axis; `wedge` from an inner ring (zero-based length) |
| k | `waffle`, `unit-bars`, `single-100-bar`, `treemap`, `circle-pack`, `dot-plot` | unit squares; unit rows; one segmented bar; `d3.treemap`; `d3.pack` (area = value) |
| g | `heatmap`, `3d-terrain`, `small-multiple-lines`, `ridgeline` | cells; boxes with height (§5); slices per panel; overlapping area slices per row |

## 4. Moving between forms

Smooth means every mark travels continuously from where it is to where it's going: no jumps, no stops halfway, no cuts. Frame rate is rarely the problem (a few hundred polygons morph at full speed in SVG); motion design is.

- **Never place marks instantly on a scene change.** Duration 0 is only for the first paint, a resize, or reduced motion. A form whose layout "isn't ready" waits for its data; it doesn't snap.
- **One continuous move per change.** If two forms differ in more than one way (position *and* size *and* color), overlap the steps instead of running them one after another: color starts when the move is half done, size a quarter in. No pauses between steps, and the whole change stays under the tempo's duration.
- **Between reels, bridge instead of cutting.** The outgoing marks collapse toward the places where the incoming marks will appear (their baseline, their centre, or the shared axis), and the incoming marks grow out of those same places while the outgoing ones are still fading. Never fade the stage to empty and redraw.
- **Start from what's on screen.** Every transition starts from the points currently drawn (the snippet in §2 keeps them), so a click mid-morph changes course instead of jumping.
- **Keep point order stable** across forms (every outline starts at its top-left corner and runs clockwise) or the marks twist as they move.
- **Stagger gently:** the seed's `motion.stagger` order, with the whole stagger at most 25% of the duration (1–4 ms per mark). A long stagger reads as marks lagging, not flowing.
- **Easing** from the seed's `motion.easing`; durations from `motion.tempo`: brisk 700 ms, measured 1,100 ms, slow-reveal 1,600 ms per change.
- **Guides crossfade with the marks:** the old axes and labels fade during the first third, the new ones during the last third, in the same transition, so the text never pops.
- **Same marks, new measure.** A scene may switch the measure (requests → seconds to first token) only when its title and axis say so and the axis label changes with the marks.
- **Filters** re-run the current form's layout with the update transition (`motion.md`, Timing); Play glides (`motion.md`, Glide) in every form.
- **Lots of marks** (more than ~2,000 polygons, or measured frames over 20 ms): paint the marks on a `<canvas>` with one `d3.timer` interpolating Float32Array points, and keep SVG for guides and hover targets updated when the morph ends.

## 5. 3D in SVG with d3-3d

d3-3d projects 3D points to the screen; its output is plain polygons, so 3D forms plug into the polygon engine and morph to and from 2D.

```js
import { polygons3D } from "https://cdn.jsdelivr.net/npm/d3-3d@1.0.0/+esm";
const proj = polygons3D().origin({ x: W / 2, y: H * 0.62 }).scale(s).rotateY(yaw).rotateX(pitch);
const box = (x0, z0, w, d, h) => {                                // corners in data space: x = period, z = category, y up = value
  const P = (x, y, z) => ({ x, y: -y, z });                       // d3-3d's y points down
  return {                                                        // each face starts at its top-left corner, like rect()
    front: [P(x0, h, z0 + d), P(x0 + w, h, z0 + d), P(x0 + w, 0, z0 + d), P(x0, 0, z0 + d)],
    top: [P(x0, h, z0), P(x0 + w, h, z0), P(x0 + w, h, z0 + d), P(x0, h, z0 + d)],
    side: [P(x0 + w, h, z0 + d), P(x0 + w, h, z0), P(x0 + w, 0, z0), P(x0 + w, 0, z0 + d)],
  };
};
const faces = (b) => Object.fromEntries(Object.entries(b).map(([k, quad]) => [k, resample(proj([quad])[0].map((v) => [v.projected.x, v.projected.y]))]));
```

- Sort marks back to front after projecting (by the box's rotated z), so near boxes paint over far ones. In d3-3d a larger `rotated.z` is nearer the viewer: sort ascending and append in that order.
- The faces above are the ones seen from the +z, +x side. Once the yaw can turn the box the other way, pick each pair's nearer face: project a probe (`P(0,0,1)` against `P(0,0,-1)`, `P(1,0,0)` against `P(-1,0,0)`) and use `z0 + d` or `z0` for the front, `x0 + w` or `x0` for the side, by whichever has the larger `rotated.z`. Otherwise the drawn faces are the hidden ones and the boxes look inside out.
- d3-3d's projection is orthographic: `projected = origin + scale × rotated`. Fit `scale` and `origin` once per stage size (project the bounding box at scale 1) and keep them while dragging, so the scene doesn't zoom as it turns.
- Drag on the stage rotates (`yaw`, `pitch` within limits that keep the floor visible); re-project without transition while dragging.
- Shade faces from one fill: top lightest, front as is, side darkest, so the box reads without lighting maths.
- The honest-3D rules in `stage.md` §5 apply: three data axes, height linear from zero, color repeating height or category, exact values on hover, a floor grid with axis labels. More than ~2,000 boxes, use three.js instead (`stage.md` §5); d3-3d is for morphable 3D.

## 6. Icons

Use the icon font pinned in `guidelines/dashboard.md` (Tabler): `<i class="ti ti-player-play" aria-hidden="true"></i>`. Icons mark scenes, controls, categories and KPI labels; they never encode a quantity and never replace a text label for something the reader must read. Pick each icon for its meaning in this dashboard; the seed's `icons.weight` says whether accents use the filled style.

## 7. Checks

Step through every chain forwards and backwards, with a filter on, while Play runs, and with motion off. Every form must pass the honesty pass on its own (`visual-language.md` Part 4).

**Motion check.** Expose `window.__dash = { showScene, SCENES }` on the page, then run this in the page (console or the browser tool) with motion on. It moves through every scene and measures how the marks travel. Fix every scene it flags before sharing.

```js
// Flags scene changes that cut (nothing travels), jump (more than 80 px in one frame) or finish too fast to see (under 400 ms).
// Keep the same mark elements across scenes: replacing them reads as a cut here and on screen.
// Run it with the browser tab in front: hidden tabs pause requestAnimationFrame and every scene reads as a cut.
// Start it from scene 1. It checks every mark; with thousands of marks it takes a few seconds per scene.
async function motionCheck({ settle = 2600 } = {}) {
  const box = (el) => { const b = el.getBBox(); return [b.x + b.width / 2, b.y + b.height / 2, Math.sqrt(b.width * b.height)]; };
  const out = [];
  const n = window.__dash.SCENES.length;
  for (const i of [...Array(n).keys()].slice(1).concat(0)) {   // end on scene 1, so every change (including back to the start) is measured
    const before = new Set(document.querySelectorAll("svg path, svg rect, svg circle"));
    window.__dash.showScene(i);
    const t0 = performance.now(), frames = [];
    await new Promise((done) => { const tick = () => {
      const marks = [...document.querySelectorAll("svg path, svg rect, svg circle")].filter((el) => before.has(el) || frames.length);
      frames.push({ t: performance.now() - t0, m: new Map(marks.map((el) => [el, box(el)])) });
      performance.now() - t0 < settle ? requestAnimationFrame(tick) : done(); }; requestAnimationFrame(tick); });
    let jump = 0, last = 0;
    for (let k = 1; k < frames.length; k++) for (const [el, c] of frames[k].m) { const p = frames[k - 1].m.get(el); if (!p) continue;
      const d = Math.hypot(c[0] - p[0], c[1] - p[1]) + Math.abs(c[2] - p[2]); if (d > 0.5) last = frames[k].t; jump = Math.max(jump, d); }
    const verdict = last === 0 ? "cut: nothing travelled (geometry set instantly, or new elements replaced the old)"
      : last < 400 ? "too fast to follow" : jump > 80 ? "jump: a mark moved more than 80 px in one frame" : "ok";
    out.push({ scene: i + 1, maxPxPerFrame: Math.round(jump), movedForMs: Math.round(last), verdict });
  }
  console.table(out); return out;
}
```

80 px per frame is a fast but continuous move at 60 Hz on a full-screen stage; anything above is a jump. 400 ms is about the shortest change the eye follows as motion rather than a cut. Record the table in `5-handoff/handoff.md`.
