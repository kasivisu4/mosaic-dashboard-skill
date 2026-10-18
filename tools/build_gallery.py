"""Publish finished dashboard runs into docs/gallery/, with an index page that shows them as cards.

Usage (from the repo root):
  python tools/build_gallery.py RUN[=LABEL] [RUN[=LABEL] ...]
  e.g. python tools/build_gallery.py skills/planning-dashboard/out/chutes-reel-opus="Claude Opus 5.5"

For each run folder it copies 4-dashboard/index.html, the data files listed in plan.md's header, plan.md,
2-intake/brief.md and 5-handoff/report.html (when small enough) into docs/gallery/<run name>/, records the
run's title, design seed and scene count in docs/gallery/gallery.json, and regenerates docs/gallery/index.html.
Runs already in gallery.json and not named again are kept. GitHub Pages serving /docs then gives every
dashboard a public link; the pages fetch their data over https, so no server of your own is needed.
"""
import html
import json
import re
import shutil
import sys
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "skills" / "planning-dashboard" / "scripts"))
from plan_format import parse  # noqa: E402

GALLERY = ROOT / "docs" / "gallery"
# GitHub warns above 50 MB per file and refuses 100 MB; a shareable report over 15 MB is better left out
# (the live page already works on Pages, and bundle_report.py's own limit is 15 MB).
MAX_REPORT_MB = 15


def die(msg):
    print(f"build_gallery: {msg}", file=sys.stderr)
    sys.exit(1)


def add_run(arg):
    path, _, label = arg.partition("=")
    run = (ROOT / path).resolve() if not Path(path).is_absolute() else Path(path)
    dash = run / "4-dashboard"
    for need in (dash / "index.html", dash / "plan.md"):
        if not need.exists():
            die(f"{need} is missing; finish the run first (SKILL.md step 5)")
    text = (dash / "plan.md").read_text(encoding="utf-8")
    plan, errors = parse(text)
    if errors:
        die(f"{dash / 'plan.md'} doesn't validate: {errors[0]}")
    dest = GALLERY / run.name
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    shutil.copy2(dash / "index.html", dest / "index.html")
    shutil.copy2(dash / "plan.md", dest / "plan.md")
    for f in plan.get("files", []):
        src = dash / str(f["file"])
        if not src.exists():
            die(f"plan.md lists {f['file']}, but {src} doesn't exist")
        shutil.copy2(src, dest / src.name)
    brief = run / "2-intake" / "brief.md"
    if brief.exists():
        shutil.copy2(brief, dest / "brief.md")
    report = run / "5-handoff" / "report.html"
    has_report = report.exists() and report.stat().st_size <= MAX_REPORT_MB * 1e6
    if has_report:
        shutil.copy2(report, dest / "report.html")
    seed = {}
    seeds = sorted((run / "3-layout").glob("design-seed.json"))
    if seeds:
        seed = json.loads(seeds[0].read_text(encoding="utf-8"))
    usage = {}
    if (run / "5-handoff" / "usage.json").exists():
        usage = json.loads((run / "5-handoff" / "usage.json").read_text(encoding="utf-8"))
    title = re.search(r"^#\s+(.+)$", text, flags=re.M)
    takeaway = text.split(title.group(0), 1)[1].strip().split("\n## ", 1)[0].strip() if title else ""
    return {
        "name": run.name, "label": label or "", "title": title.group(1).strip() if title else run.name,
        "takeaway": takeaway, "scenes": len(plan.get("charts", [])), "goals": plan.get("goals", []),
        "concept": seed.get("concept", ""), "theme": seed.get("theme", ""), "palette": seed.get("palette", ""),
        "colors": seed.get("colors", []), "provocations": seed.get("provocations", []),
        "has_report": has_report, "has_brief": brief.exists(), "added": date.today().isoformat(),
        "model": usage.get("model", ""), "skill_version": usage.get("skill_version", ""), "tokens": usage.get("tokens"),
        "cost_usd": usage.get("cost_usd"), "cost_range_usd": usage.get("cost_range_usd"), "usage_note": usage.get("note", ""),
    }


SCRIPT = """<script>
  const cards = [...document.querySelectorAll(".card")], grid = document.getElementById("grid");
  const groups = { model: "Model", concept: "Layout", version: "Skill version" }, on = { model: new Set(), concept: new Set(), version: new Set() };
  const chips = document.getElementById("chips");
  for (const [k, label] of Object.entries(groups)) {
    const vals = [...new Set(cards.map((c) => c.dataset[k]).filter(Boolean))].sort();
    if (!vals.length) continue;
    const g = document.createElement("span"); g.className = "group"; g.innerHTML = `<b>${label}</b>`;
    for (const v of vals) { const b = document.createElement("button"); b.type = "button"; b.textContent = v.replace(/^claude-/, "");
      b.setAttribute("aria-pressed", "false"); b.onclick = () => { on[k].has(v) ? on[k].delete(v) : on[k].add(v); b.setAttribute("aria-pressed", String(on[k].has(v))); apply(); }; g.append(b); }
    chips.append(g);
  }
  const num = (c, k) => (c.dataset[k] === "" ? Infinity : +c.dataset[k]);
  function apply() {
    const q = document.getElementById("q").value.trim().toLowerCase(), sort = document.getElementById("sort").value;
    let shown = 0;
    for (const c of cards) { const ok = (!q || c.dataset.text.includes(q)) && Object.keys(on).every((k) => !on[k].size || on[k].has(c.dataset[k])); c.hidden = !ok; shown += ok; }
    const order = [...cards];
    if (sort === "cost" || sort === "tokens") order.sort((a, b) => num(a, sort) - num(b, sort));
    if (sort === "scenes") order.sort((a, b) => num(b, "scenes") - num(a, "scenes"));
    order.forEach((c) => grid.append(c));
    document.getElementById("count").textContent = `${shown} of ${cards.length} dashboards`;
  }
  // Live thumbnails: each card's real dashboard, scaled down. Loaded on hover, focus or tap; at most two alive,
  // since every preview starts its own DuckDB engine and loads its data.
  const LIVE_MAX = 2, live = [];
  function preview(box) {
    if (box.querySelector("iframe")) return;
    while (live.length >= LIVE_MAX) { const old = live.shift(); old.querySelector("iframe")?.remove(); old.querySelector(".ph").hidden = false; }
    const f = document.createElement("iframe"); f.src = box.dataset.src; f.title = "Live preview"; f.loading = "eager"; f.tabIndex = -1;
    const fit = () => { f.style.transform = `scale(${box.clientWidth / 1280})`; };
    fit(); new ResizeObserver(fit).observe(box);
    f.onload = () => setTimeout(() => { f.classList.add("ready"); box.querySelector(".ph").hidden = true; }, 1500);
    box.append(f); live.push(box);
  }
  document.querySelectorAll(".thumb").forEach((box) => {
    box.addEventListener("mouseenter", () => preview(box));
    box.addEventListener("focus", () => preview(box));
    box.addEventListener("click", () => box.querySelector("iframe.ready") ? location.assign(box.dataset.src) : preview(box));
  });
  document.getElementById("q").oninput = apply; document.getElementById("sort").onchange = apply; apply();
</script>"""


def page(runs):
    e = html.escape
    cards = []
    for r in runs:
        sw = "".join(f'<i style="background:{e(c)}"></i>' for c in r["colors"][:6])
        meta = " · ".join(x for x in [r["label"], r["concept"] and f"{r['concept']} layout", f"{r['scenes']} scenes", r["palette"] and f"{r['palette']} palette"] if x)
        prov = "".join(f"<li>{e(p)}</li>" for p in r["provocations"])
        links = [f'<a class="primary" href="{e(r["name"])}/index.html">Open dashboard</a>']
        if r["has_report"]:
            links.append(f'<a href="{e(r["name"])}/report.html" download>Download report.html</a>')
        links.append(f'<a href="{e(r["name"])}/plan.md">Plan</a>')
        if r["has_brief"]:
            links.append(f'<a href="{e(r["name"])}/brief.md">Brief</a>')
        if r.get("tokens"):
            rng = f" (est. ${r['cost_range_usd'][0]}–${r['cost_range_usd'][1]})" if r.get("cost_range_usd") else ""
            usage = f"{r['tokens']:,} tokens · about ${r['cost_usd']}{rng}"
        else:
            usage = "tokens not measured"
        ver = f"skill {r['skill_version']}" if r.get("skill_version") else ""
        model = r.get("model", "")
        cards.append(f"""<article class="card" data-model="{e(model)}" data-concept="{e(r['concept'])}" data-version="{e(r.get('skill_version',''))}" data-cost="{r.get('cost_usd') or ''}" data-tokens="{r.get('tokens') or ''}" data-scenes="{r['scenes']}" data-text="{e((r['title'] + ' ' + r['takeaway']).lower())}">
  <div class="thumb" tabindex="0" data-src="{e(r["name"])}/index.html" aria-label="Live preview of {e(r["title"])}: hover or focus to load">
    <div class="ph"><div class="swatches">{sw}</div><span>Hover for a live preview</span></div>
  </div>
  <h2>{e(r["title"])}</h2>
  <p class="meta">{e(meta)}</p>
  <p class="take">{e(r["takeaway"])}</p>
  <p class="usage" title="{e(r.get('usage_note',''))}">{e(usage)}{(' · ' + e(ver)) if ver else ''}</p>
  {f'<details><summary>Creative constraints</summary><ul>{prov}</ul></details>' if prov else ''}
  <nav>{"".join(links)}</nav>
</article>""")
    return f"""<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>Dashboard Gallery</title>
<style>
  :root {{ --bg:#f7f6f3; --card:#ffffff; --ink:#16181c; --muted:#5f6670; --rule:#e2e0da; --accent:#2f5bd3; }}
  @media (prefers-color-scheme: dark) {{ :root:not([data-theme="light"]) {{ --bg:#0f1115; --card:#171a20; --ink:#eceef2; --muted:#9aa2ad; --rule:#272b33; --accent:#7aa2ff; }} }}
  :root[data-theme="dark"] {{ --bg:#0f1115; --card:#171a20; --ink:#eceef2; --muted:#9aa2ad; --rule:#272b33; --accent:#7aa2ff; }}
  * {{ box-sizing: border-box; }}
  body {{ margin:0; background:var(--bg); color:var(--ink); font:15px/1.55 system-ui,-apple-system,"Segoe UI",sans-serif; }}
  main {{ max-width:1160px; margin:0 auto; padding:40px 16px 64px; }}
  h1 {{ font-size:34px; line-height:1.1; margin:0 0 8px; letter-spacing:-.02em; }}
  .lede {{ color:var(--muted); max-width:70ch; margin:0 0 28px; }}
  .grid {{ display:grid; grid-template-columns:repeat(auto-fill,minmax(320px,1fr)); gap:16px; }}
  .card {{ background:var(--card); border:1px solid var(--rule); border-radius:16px; padding:18px; display:flex; flex-direction:column; gap:8px; }}
  .swatches {{ display:flex; gap:4px; width:70%; }} .swatches i {{ flex:1; height:10px; border-radius:5px; }}
  .thumb {{ position:relative; aspect-ratio:16/10; border-radius:10px; overflow:hidden; border:1px solid var(--rule); background:var(--bg); cursor:zoom-in; }}
  .thumb .ph {{ position:absolute; inset:0; display:flex; flex-direction:column; gap:10px; align-items:center; justify-content:center; color:var(--muted); font-size:12.5px; }}
  .thumb iframe {{ position:absolute; left:0; top:0; width:1280px; height:800px; border:0; transform-origin:0 0; pointer-events:none; opacity:0; transition:opacity .4s; }}
  .thumb iframe.ready {{ opacity:1; }}
  .card h2 {{ font-size:18px; line-height:1.25; margin:6px 0 0; }}
  .meta {{ color:var(--muted); font-size:13px; margin:0; }}
  .take {{ margin:0; font-size:14px; flex:1; }}
  details {{ font-size:13px; color:var(--muted); }} details ul {{ margin:6px 0 0; padding-left:18px; }}
  nav {{ display:flex; flex-wrap:wrap; gap:8px; margin-top:6px; }}
  nav a {{ font-size:13px; color:var(--ink); text-decoration:none; border:1px solid var(--rule); border-radius:8px; padding:5px 10px; }}
  nav a.primary {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
  nav a:hover {{ border-color:var(--accent); }}
  footer {{ color:var(--muted); font-size:13px; margin-top:28px; }}
  .usage {{ margin:0; font-size:12.5px; color:var(--muted); font-variant-numeric:tabular-nums; }}
  .filters {{ display:flex; flex-wrap:wrap; gap:10px 14px; align-items:center; margin:0 0 18px; }}
  .filters input, .filters select {{ font:inherit; font-size:13px; color:var(--ink); background:var(--card); border:1px solid var(--rule); border-radius:8px; padding:6px 10px; }}
  .filters input {{ min-width:240px; }}
  .group {{ display:inline-flex; gap:4px; align-items:center; flex-wrap:wrap; margin-right:6px; }}
  .group b {{ font-size:12px; color:var(--muted); font-weight:600; margin-right:2px; }}
  .group button {{ font:inherit; font-size:12.5px; color:var(--ink); background:var(--card); border:1px solid var(--rule); border-radius:999px; padding:3px 10px; cursor:pointer; }}
  .group button[aria-pressed="true"] {{ background:var(--accent); border-color:var(--accent); color:#fff; }}
  .card[hidden] {{ display:none; }}
</style></head>
<body><main>
<h1>Dashboard gallery</h1>
<p class="lede">Dashboards generated by the planning-dashboard skill, each designed from scratch from a fresh design seed: its own layout, chart forms, palette and motion. Every page runs in your browser with DuckDB-WASM, Mosaic and D3; the plan and brief show how each one was decided.</p>
<div class="filters" id="filters">
  <input type="search" id="q" placeholder="Search titles and findings" aria-label="Search dashboards">
  <span id="chips"></span>
  <select id="sort" aria-label="Sort"><option value="">Newest first</option><option value="cost">Cheapest first</option><option value="tokens">Fewest tokens first</option><option value="scenes">Most scenes first</option></select>
  <span id="count" class="meta"></span>
</div>
<section class="grid" id="grid">
{chr(10).join(cards)}
</section>
{SCRIPT}
<footer>Costs are estimates from total token counts (see each run's usage.json for the basis); hover a cost for notes. Built with <code>python tools/build_gallery.py</code>. Data: see each dashboard's technical notes for its source.</footer>
</main></body></html>
"""


def main(argv):
    if len(argv) < 2:
        die("usage: python tools/build_gallery.py RUN[=LABEL] [RUN[=LABEL] ...]")
    GALLERY.mkdir(parents=True, exist_ok=True)
    index_json = GALLERY / "gallery.json"
    runs = json.loads(index_json.read_text(encoding="utf-8")) if index_json.exists() else []
    for arg in argv[1:]:
        r = add_run(arg)
        runs = [x for x in runs if x["name"] != r["name"]] + [r]
        print(f"added {r['name']}: {r['title']} ({r['scenes']} scenes{', report.html' if r['has_report'] else ''})")
    index_json.write_text(json.dumps(runs, indent=2), encoding="utf-8")
    (GALLERY / "index.html").write_text(page(runs), encoding="utf-8")
    print(f"wrote {GALLERY / 'index.html'} with {len(runs)} dashboard(s)")


if __name__ == "__main__":
    main(sys.argv)
