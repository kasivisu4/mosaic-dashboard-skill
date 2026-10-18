"""Pick a fresh design for a dashboard: layout concept, show-reel chains of chart forms, palette, theme, icons, motion.

Every run gets a different look. The script reads the design seeds of earlier runs (out/*/3-layout/design-seed*.json)
only to avoid repeating them: a concept used in the last runs, or a chain that starts with the same form.

Usage: python scripts/design_seed.py out/<name> --units cp,p,c [--seed N]
  --units  the mark units the data supports (references/show-reel.md, "Mark units"):
           cp = category x period, p = period (e.g. day), c = cycle position (e.g. hour),
           k = category, g = period x cycle grid
  --seed   repeat a draw exactly (default: random)
Writes out/<name>/3-layout/design-seed.json and prints it.
"""
import json
import random
import sys
from pathlib import Path

# Layout concepts (references/stage.md, "Layout concepts").
CONCEPTS = ["stage-rail", "scrolly-split", "cinema", "poster-hub", "magazine"]

# Honest chart forms per mark unit, and which ones morph smoothly into which (references/show-reel.md, "Form catalog").
# A chain is a walk through this graph, so every step is one small change for the eye.
GRAPH = {
    "cp": {
        "dots": ["lines", "bump", "heat-cells"],
        "lines": ["stacked-area", "dots", "small-multiple-lines"],
        "bump": ["lines", "dots"],
        "stacked-area": ["stream", "stacked-100", "stacked-bars"],
        "stream": ["stacked-area"],
        "stacked-100": ["stacked-area", "stacked-bars-100"],
        "stacked-bars-100": ["stacked-bars", "stacked-100"],
        "stacked-bars": ["grouped-bars", "3d-bars", "treemap", "stacked-bars-100"],
        "grouped-bars": ["small-multiple-bars", "stacked-bars"],
        "small-multiple-bars": ["small-multiple-lines", "grouped-bars"],
        "small-multiple-lines": ["lines", "small-multiple-bars"],
        "heat-cells": ["3d-bars", "dots"],
        "3d-bars": ["stacked-bars", "heat-cells"],
        "treemap": ["stacked-bars"],
    },
    "p": {
        "strip": ["beeswarm", "timeline-bars", "spiral"],
        "beeswarm": ["unit-histogram", "strip"],
        "unit-histogram": ["beeswarm"],
        "timeline-bars": ["calendar", "spiral", "strip", "horizon"],
        "calendar": ["timeline-bars", "spiral"],
        "spiral": ["calendar", "timeline-bars", "strip"],
        "horizon": ["timeline-bars"],
    },
    "c": {                         # no radial area: a closed polar area is a radar chart (style-system.md, Never)
        "radial-bars": ["bars"],
        "bars": ["radial-bars", "dot-plot"],
        "dot-plot": ["bars"],
    },
    "k": {
        "waffle": ["unit-bars", "single-100-bar"],
        "unit-bars": ["waffle", "dot-plot"],
        "single-100-bar": ["waffle", "treemap"],
        "treemap": ["circle-pack", "single-100-bar"],
        "circle-pack": ["treemap"],
        "dot-plot": ["unit-bars"],
    },
    "g": {
        "heatmap": ["3d-terrain", "small-multiple-lines", "ridgeline"],
        "3d-terrain": ["heatmap"],
        "small-multiple-lines": ["heatmap", "ridgeline"],
        "ridgeline": ["small-multiple-lines", "heatmap"],
    },
}
# Chain lengths: the first unit carries the main show reel; later units get shorter reels.
MAIN_CHAIN, SIDE_CHAIN = (5, 8), (2, 4)
# Recent runs to avoid repeating, newest first.
HISTORY = 3

# Color-blind-safe categorical palettes (max 6 hues; the rest fold into muted "other").
PALETTES = {
    "okabe-ito": ["#0072b2", "#e69f00", "#009e73", "#cc79a7", "#56b4e9", "#d55e00"],
    "tableau": ["#4e79a7", "#f28e2b", "#59a14f", "#e15759", "#76b7b2", "#b07aa1"],
    "dark2": ["#1b9e77", "#d95f02", "#7570b3", "#e7298a", "#66a61e", "#e6ab02"],
    "observable": ["#4269d0", "#efb118", "#ff725c", "#6cc5b0", "#3ca951", "#ff8ab7"],
}
THEMES = {
    "paper": {"bg": "#f7f5f0", "panel": "#efece4", "ink": "#1f1d1a", "muted": "#6e6a62", "rule": "#ddd8cc"},
    "midnight": {"bg": "#0b0d12", "panel": "#131722", "ink": "#e9ecf2", "muted": "#8d95a5", "rule": "#232a38"},
    "slate": {"bg": "#14181d", "panel": "#1b2027", "ink": "#e6e8eb", "muted": "#98a0aa", "rule": "#2a313a"},
    "studio": {"bg": "#ffffff", "panel": "#f4f6f8", "ink": "#111418", "muted": "#5f6b78", "rule": "#e3e7ec"},
}
MOTION = {
    "stagger": ["left-to-right", "centre-out", "by-rank", "by-category"],
    "easing": ["cubicInOut", "quadInOut", "sinInOut", "expOut"],
    "tempo": ["brisk", "measured", "slow-reveal"],
}
# Creative constraints, drawn two per run. They push past the catalogs (lists anchor; constraints invent).
# All are data-agnostic and compatible with the honesty rules.
PROVOCATIONS = [
    "The hero has no axes: values are read from labels, counts or position against a reference.",
    "One mark is one unit (a day, a bucket of N, one percent); totals are counts you can see.",
    "The story is carried by a single moving object or playhead the reader can follow.",
    "Use a physical metaphor for the main change: filling, draining, stacking, flowing, eroding.",
    "Marks regroup physically between scenes (force layout), never fading out and in.",
    "The first scene is a single number that unfolds into the data behind it.",
    "Compare by alignment: every scene lines its marks up against the same baseline or ring.",
    "Let the reader's pointer reveal a hidden layer (a lens, a scrubber, a split view).",
    "Show the whole dataset first as one texture, then zoom into the pattern that matters.",
    "Use space as time: a path, spiral or road the reader travels along.",
    "Every category gets its own small world (small multiples) that later merge into one.",
    "Color is used for one thing only; everything else is ink and position.",
]
# Scenes per page whose form must be invented (in no catalog), justified by the data's shape.
INVENTED_SCENES = 1
ICONS = {"set": "tabler", "weight": ["outline", "filled-accents"], "use": ["scene markers", "controls", "category chips", "KPI labels"]}


def die(msg):
    print(f"design_seed: {msg}", file=sys.stderr)
    sys.exit(1)


def history(out_dir):
    """Earlier seeds, newest first, from every run folder next to this one."""
    seeds = []
    own = (Path(out_dir) / "3-layout" / "design-seed.json").resolve()   # the seed this run is about to replace
    for f in Path(out_dir).parent.glob("*/3-layout/design-seed*.json"):
        if f.resolve() == own:
            continue
        try:
            seeds.append((f.stat().st_mtime, json.loads(f.read_text(encoding="utf-8"))))
        except (OSError, json.JSONDecodeError) as e:
            print(f"design_seed: skipped unreadable {f}: {e}", file=sys.stderr)
    return [s for _, s in sorted(seeds, key=lambda t: -t[0])][:HISTORY]


def walk(rng, graph, length, avoid_start):
    starts = [f for f in graph if f not in avoid_start] or list(graph)
    for _ in range(200):           # retry until a walk of the wanted length exists without repeats
        chain = [rng.choice(starts)]
        while len(chain) < length:
            nxt = [f for f in graph[chain[-1]] if f not in chain]
            if not nxt:
                break
            chain.append(rng.choice(nxt))
        if len(chain) == length:
            return chain
    return chain


def main(argv):
    if len(argv) < 2 or argv[1].startswith("-"):
        die("usage: python scripts/design_seed.py out/<name> --units cp,p,c [--seed N]")
    run = Path(argv[1])
    if not run.is_dir():
        die(f"{run} is not a run folder; create it with start_run.py or run_folder.py init")
    args = dict(zip(argv[2::2], argv[3::2]))
    units = [u.strip() for u in args.get("--units", "").split(",") if u.strip()]
    bad = [u for u in units if u not in GRAPH]
    if not units or bad:
        die(f"--units needs one or more of {sorted(GRAPH)}; got {args.get('--units')!r}")
    seed = int(args["--seed"]) if "--seed" in args else random.SystemRandom().randrange(10**9)
    rng = random.Random(seed)
    past = history(run)
    used_concepts = [s.get("concept") for s in past]
    used_starts = {u: {s.get("chains", {}).get(u, [None])[0] for s in past} for u in units}
    concept = rng.choice([c for c in CONCEPTS if c not in used_concepts] or CONCEPTS)
    chains = {}
    for i, u in enumerate(units):
        lo, hi = MAIN_CHAIN if i == 0 else SIDE_CHAIN
        chains[u] = walk(rng, GRAPH[u], rng.randint(lo, min(hi, len(GRAPH[u]))), used_starts[u])
    palette = rng.choice([p for p in PALETTES if p not in [s.get("palette") for s in past]] or list(PALETTES))
    theme = rng.choice([t for t in THEMES if t not in [s.get("theme") for s in past]] or list(THEMES))
    out = {
        "seed": seed, "concept": concept, "chains": chains, "palette": palette, "colors": PALETTES[palette],
        "theme": theme, "theme_colors": THEMES[theme],
        "motion": {k: rng.choice(v) for k, v in MOTION.items()},
        "icons": {"set": ICONS["set"], "weight": rng.choice(ICONS["weight"]), "use": ICONS["use"]},
        "provocations": rng.sample(PROVOCATIONS, 2),
        "invented_scenes": INVENTED_SCENES,
        "note": "Chains are starting points, not limits: reorder, cut, or replace forms when the data asks for it, and invent at least one form no catalog names (question-brief.md section 3).",
        "avoided": {"concepts": used_concepts, "chain_starts": {u: sorted(x for x in s if x) for u, s in used_starts.items()}},
    }
    (run / "3-layout").mkdir(parents=True, exist_ok=True)
    (run / "3-layout" / "design-seed.json").write_text(json.dumps(out, indent=2), encoding="utf-8")
    print(json.dumps(out, indent=2))


if __name__ == "__main__":
    main(sys.argv)
