# The stage: a one-screen dashboard that morphs through scenes

A stage is a dashboard that fits one screen and never scrolls. One large canvas holds a persistent set of marks, and the page moves through **scenes**: each scene is one angle from the brief, and moving to the next re-forms the same marks into the next chart. Think of D3's Show Reel, where one dataset flows from lines to areas to stacks to bars to a pie and never leaves the screen, but where every view answers a question and passes the honesty rules.

Use it with `surface: stage` in the plan's Style (typically with the `impact` goal). Each story line after the KPIs is one scene, in order.

## Contents
- 1. Layout
- 2. Design the scenes
- 3. Mark units and acts
- 4. Transitions between scenes
- 5. 3D scenes (WebGL)
- 6. Navigation and filters
- 7. Checks

## 1. Layout

The design seed picks a **layout concept**. They share the rules below (one screen, scenes, filters everywhere) but look and read differently:

| Concept | What it looks like |
|---|---|
| `stage-rail` | stage on the left, a side rail with KPIs, filters, time strip and scene list |
| `scrolly-split` | a narrative column of scene cards on one side; the stage stays pinned while the reader scrolls, each card triggers its scene |
| `cinema` | full-bleed stage; title and caption as a lower third; a transport bar at the bottom (icons for previous, play, next, autoplay, scene chapters); KPIs and filters in a slim top bar |
| `poster-hub` | a large central stage with scene icons arranged around it; the active icon expands into the title |
| `magazine` | big editorial type, the stage interleaved with pull-quotes of each finding; filters in a floating pill |

The sketch below is `stage-rail`; adapt the regions for the others.


```
┌──────────────────────────────────────────────────────────┬──────────────┐
│ scene title (the finding)                     ● ● ○ ○ ○  │ KPIs (count- │
│ caption                                                  │ up, sparks)  │
│                                                          │ filters      │
│                    STAGE (marks persist)                 │ time strip   │
│                                                          │ + Play       │
│ guides / legend for this scene                           │ scene list   │
│ ◀ prev   ▶ autoplay   next ▶                             │ notes ⓘ      │
└──────────────────────────────────────────────────────────┴──────────────┘
```

- `100dvh` tall, no page scroll. The stage takes the remaining space and is redrawn at its real size on resize.
- The scene title and caption have a fixed height (two lines for the title), so a title that wraps differently doesn't resize the stage mid-morph. Resize redraws animate, or wait for a running morph to end; a redraw at duration 0 cuts the morph.
- Overlays that aren't data marks (lens, crosshair, brush) carry `data-motion-ignore`, so the motion check (`show-reel.md` §7) skips them.
- The **rail** holds what stays true across scenes: the KPIs (`motion.md` §4), the filters and their chips, a small time strip with a brush and Play, and the scene list (each entry is the scene's short name; the current one is marked).
- Technical notes open in a drawer from the rail, not below the fold.
- On phones the rail collapses to a bar above the stage, and scenes advance by swipe as well.

## 2. Design the scenes

Generate the scenes from the brief, fresh for this data, following the seed's chains of forms (`references/show-reel.md`); never reuse another dashboard's sequence.

1. Start from the brief's angles. Each supporting question can give one or more scenes; the hook gets the first scene of the second act or the opening scene, wherever it lands with the most force.
2. For each angle, list the honest views of its data (`visual-language.md` Part 2) and keep 1–3 that each show something the previous one didn't. "Calendar, then the same days as a timeline" is a scene pair; "the same chart in another color" isn't.
3. Order scenes so each transition is a small step for the eye: same marks, one change at a time (position, then size, then color).
4. Aim for 6–12 scenes in 2–4 acts. Fewer than 6 is a grid, not a stage; more than 12 loses the reader.
5. Every scene has a finding-title computed from the data, a one-sentence caption, its guides (axes, legend, scale note), and an `@` moment if it has one.

Write each scene as a story line with its `~ draw:` line naming the view and the transition into it, e.g. `~ draw: day squares slide from the calendar into a daily bar timeline`.

## 3. Mark units and acts

A **mark unit** is the thing one mark stands for: a day, an hour, a category-month, one percent. Scenes that share a unit form an **act**, and within an act the marks morph. Pick units from the data's grain and the angles:

| Unit | Views it can morph through (examples) |
|---|---|
| day (or week) | calendar heatmap → daily bar timeline → dot histogram of days by volume → weekday cycle |
| category × period | bump (rank) → share lines → 100% stacked columns → period totals as one bar per category built from its periods |
| category × period cells | heat strips of measure A → heat strips of measure B (same cells, new scale and legend) |
| cycle position (hour, weekday) | radial clock → straight bars |
| unit of 1% | waffle → unit bars → one 100% bar |
| day × cycle (e.g. day × hour) | 2D heatmap seen from above → 3D terrain that rises (§5) |

Between acts, marks of one unit can **split or merge** into the next when the math is honest (days summed into hours: each day-hour column slides into its hour's column), or the old marks fade out while the new ones grow in. Never pretend one unit becomes another when the numbers don't add up.

Implement each act as one keyed mark set with a `layout` per scene (`motion.md` §6). A scene object holds the act, title, caption, the layout function, and a `guides(scene)` that draws its axes and legend.

```js
const scenes = [
  { act: "days", key: "calendar", title, caption, layout: (d) => ({ x, y, w, h, rx, fill }) , guides: drawCalendarGuides },
  { act: "days", key: "timeline", ... },
  { act: "grid3d", key: "skyline", ... },   // a WebGL scene, §5
  ...
];
```

## 4. Transitions between scenes

- **Within an act:** stage the morph in 2–3 steps (`motion.md` §6): move, then resize, then recolor; old guides fade out first, new guides fade in last. 1–1.6 s in total.
- **Between acts:** the outgoing marks leave in the direction of the next view (shrink to a baseline, or fly to where the next marks will appear), then the incoming act grows in. 0.8–1.2 s.
- **Stagger** by the mark's position in the target view (left to right, or by rank), 3–10 ms per mark, so the eye can follow the wave.
- A filter change mid-scene uses the update transition (`motion.md`, Timing); a scene change while a filter is active keeps the filter.
- Autoplay waits for the reader: each scene holds for its reading time (about 4 s plus 0.3 s per caption word) and pauses on any interaction.

## 5. 3D scenes (WebGL)

3D is allowed in exactly one case: **all three axes are data**, for example day × hour × requests. The third dimension then shows a real surface, not a decoration. Rules (they extend `visual-language.md` Part 3):

- The scene starts as its honest 2D version (the camera looks straight down at a heatmap) and rises into 3D as a transition, so the reader knows what they are looking at.
- The camera can be rotated (orbit) and reset; the default angle doesn't hide the tallest values behind others.
- Height is linear in the value and starts at zero; color repeats the height (redundant encoding), with a legend.
- Exact values are one hover away (raycast to the column, show date, hour, value).
- Never 3D for a single categorical measure: no 3D bars of one category axis, no 3D pies, no extruded maps of one number. 3D bars on a grid of two data dimensions (category × period, day × hour) are the three-axis case and are allowed.

Build with three.js (pinned in `guidelines/dashboard.md`) as a Mosaic client: one `InstancedMesh` of boxes (one instance per cell), heights tweened with D3's timer so the rise, filters and Play animate like the SVG scenes. Use an import map so three's add-ons resolve:

```html
<script type="importmap">{ "imports": { "three": "https://cdn.jsdelivr.net/npm/three@0.160.0/build/three.module.js",
  "three/addons/": "https://cdn.jsdelivr.net/npm/three@0.160.0/examples/jsm/" } }</script>
```

```js
import * as THREE from "three";
import { OrbitControls } from "three/addons/controls/OrbitControls.js";
const mesh = new THREE.InstancedMesh(new THREE.BoxGeometry(1, 1, 1), new THREE.MeshStandardMaterial({ vertexColors: false }), n);
const m = new THREE.Matrix4();
function setHeights(h) {               // h[i] in scene units, ≥ 0
  for (let i = 0; i < n; i++) { m.makeScale(cellW, Math.max(h[i], 0.001), cellD); m.setPosition(x[i], h[i] / 2, z[i]); mesh.setMatrixAt(i, m); }
  mesh.instanceMatrix.needsUpdate = true;
}
// Rise: tween every height from 0 (or the previous value) to the target with d3.timer + d3.easeCubicInOut,
// and the camera from the top view to the orbit view over the same time.
```

Render only while something moves (a tween, an orbit drag, a filter update) to keep the page cool and battery-friendly. Size the renderer to the stage and update it on resize. Without WebGL (a rare old browser), show the 2D heatmap scene instead and say so.

## 6. Navigation and filters

- Next and previous by buttons, arrow keys, the scene list and swipe; autoplay toggles with the space bar. The URL hash holds the scene (`#skyline`) so a link opens on it.
- Filters live in the rail and apply to every scene; every mark set is a Mosaic client of the page filter, except where `motion.md` §5 allows a context view.
- Play glides (`motion.md`, Glide) and works in every scene.
- A click on a mark that represents a category filters by it, in any scene that shows categories.
- Scene titles are findings about all the data. While any filter is active, say so under the title ("The title describes all the data; the chart and the numbers follow your filters"), so a filtered screenshot never carries a claim it doesn't show.
- Context views (a calendar, a 3D terrain) that keep the whole period dim what lies outside the chosen dates, rather than hiding it.

## 7. Checks

Before sharing, step through every scene forwards and backwards, with and without a filter, with Play running, and with motion off (every scene must still be complete and correct as an end state). Run the honesty pass per scene (`visual-language.md` Part 4): each scene is a chart someone may screenshot.
