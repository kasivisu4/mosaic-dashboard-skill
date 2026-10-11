"""Print the confirmation card ("My read", layout preview, assumptions, actions) from a small JSON file.

Usage: python confirmation_card.py card.json

card.json:
{
  "read": "One plain sentence: what the page is, for whom, what's on top.",   (required)
  "goals": ["answer", "present"],          (required, ids from guidelines/goals.md, page order)
  "cadence": "monthly",                    (optional id)
  "audience": ["leadership"],              (optional ids)
  "review_depth": "deep",                  (optional id)
  "unsure": "Clear on X. Still unsure: Y.",            (optional)
  "assumptions": [{"name": "Comparison period", "value": "Q3 vs Q2"}],   (3-5, fuzzy first)
  "changed": ["Comparison period"],        (optional: assumption names to mark as just changed)
  "success_criteria": "top 3 drivers visible at a glance",               (optional)
  "questions": ["Is there a target for the return rate?"],               (optional, at most 3)
  "after_build": false                     (true for quick depth: "Here's what I assumed")
}

Pass the printed HTML unchanged to the inline widget. Labels come from guidelines/goals.md,
so no ids appear on the card. Buttons send: "Looks right, build it", "Adjust the plan",
"Change assumption: <name>", and each question's text.
"""
import html
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from goal_tables import goal_cards, labels, read_tables  # noqa: E402

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "confirmation-card.html"
e = html.escape
W = 600  # wireframe viewBox width; it scales to the card
CHIP = ('      <span style="font-size: 12px; padding: 3px 10px; border-radius: var(--radius); '
        'background: var(--bg-accent); color: var(--text-accent);">{}</span>')


def button(label, send, primary=False):
    style = ' style="background: var(--fill-primary); color: var(--on-primary); border: none;"' if primary else ""
    return f'    <button type="button" data-send="{e(send, quote=True)}"{style}>{e(label)} ↗</button>'


def order_goals(goals):
    """monitor always on top, present always at the bottom, the rest in the person's order."""
    middle = [g for g in goals if g not in ("monitor", "present")]
    return (["monitor"] if "monitor" in goals else []) + middle + (["present"] if "present" in goals else [])


def wireframe(goals, cadence):
    """A small SVG stacking one block per goal. Density follows cadence (daily sparse, one-time rich)."""
    tiles = {"daily": 2, "weekly": 3, "monthly": 4, "one-time": 6}.get(cadence, 4)
    parts, y = [], 8

    def label(text):
        nonlocal y
        parts.append(f'<text class="ts" x="8" y="{y + 12}">{e(text)}</text>')
        y += 20

    def row(n, h, gap=8):
        nonlocal y
        w = (W - 16 - gap * (n - 1)) / n
        for i in range(n):
            parts.append(f'<rect class="c-gray" x="{8 + i * (w + gap):.0f}" y="{y}" width="{w:.0f}" height="{h}" rx="4"/>')
        y += h + 8

    for g in order_goals(goals):
        if g == "monitor":
            label("Status vs target")
            row(3, 26)
            row(1, 18)
        elif g == "answer":
            label("Headline answer")
            row(1, 22)
            row(3, 36)
            row(2, 70)
        elif g == "explore":
            label("Explore")
            row(1, 16)
            row(min(tiles, 3), 52)
            if tiles > 3:
                row(tiles - 3, 52)
            if cadence != "daily":
                row(1, 40)
        elif g == "present":
            label("Story")
            parts.append(f'<rect class="c-gray" x="8" y="{y}" width="{W * 0.35:.0f}" height="70" rx="4"/>')
            parts.append(f'<rect class="c-gray" x="{W * 0.35 + 16:.0f}" y="{y}" width="{W - W * 0.35 - 24:.0f}" height="70" rx="4"/>')
            parts.append(f'<circle class="c-coral" cx="{W * 0.7:.0f}" cy="{y + 24}" r="5"/>')
            y += 78
        elif g == "spec":
            label("Charts as you asked")
            row(2, 70)
    return (f'    <svg width="100%" viewBox="0 0 {W} {y}" role="img"><title>Layout preview</title>'
            f'<desc>Page blocks in order: {e(", ".join(order_goals(goals)))}</desc>{"".join(parts)}</svg>')


def main():
    if len(sys.argv) != 2 or sys.argv[1] in ("-h", "--help"):
        sys.exit(__doc__)
    try:
        card = json.loads(Path(sys.argv[1]).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as err:
        sys.exit(f"Can't read {sys.argv[1]}: {err}")

    tables = read_tables()
    goal_titles = {gid: title for gid, title, _, _ in goal_cards(tables)}
    names = {"cadence": labels(tables, "Cadence"), "audience": labels(tables, "Audiences"),
             "review_depth": labels(tables, "Review depth")}

    problems = []
    if not str(card.get("read", "")).strip():
        problems.append('"read" is required: one plain sentence')
    goals = [str(g).lower() for g in card.get("goals", [])]
    if not goals or any(g not in goal_titles for g in goals):
        problems.append(f'"goals" must be 1-2 of {sorted(goal_titles)}, got {goals}')
    for key in ("cadence", "review_depth"):
        if card.get(key) and card[key] not in names[key]:
            problems.append(f'"{key}" must be one of {sorted(names[key])}, got {card[key]!r}')
    for a in card.get("audience", []):
        if a not in names["audience"]:
            problems.append(f'"audience" values must be from {sorted(names["audience"])}, got {a!r}')
    assumptions = card.get("assumptions", [])
    if not all(isinstance(a, dict) and a.get("name") and a.get("value") for a in assumptions):
        problems.append('"assumptions" entries need "name" and "value"')
    if problems:
        sys.exit("card.json problems:\n" + "\n".join(f"  - {p}" for p in problems))
    if not 3 <= len(assumptions) <= 5:
        print(f"note: {len(assumptions)} assumptions; the card reads best with 3-5", file=sys.stderr)

    chips = [goal_titles[g] for g in order_goals(goals)]
    if card.get("cadence"):
        chips.append(names["cadence"][card["cadence"]])
    chips += [names["audience"][a] for a in card.get("audience", [])]
    if card.get("review_depth"):
        chips.append(names["review_depth"][card["review_depth"]])

    changed = set(card.get("changed", []))
    rows = []
    for a in assumptions:
        mark = (' <span style="font-size: 11px; color: var(--text-accent);">changed</span>'
                if a["name"] in changed else "")
        rows.append(
            '    <div style="display: flex; align-items: center; gap: 12px; padding: 8px 0; border-top: 0.5px solid var(--border);">'
            f'<div style="flex: 1; min-width: 0; font-size: 13px;"><span style="font-weight: 500;">{e(a["name"])}</span>{mark}'
            f'<br><span style="color: var(--text-secondary);">{e(a["value"])}</span></div>'
            f'<button type="button" data-send="{e("Change assumption: " + a["name"], quote=True)}" style="font-size: 12px;">Change ↗</button></div>')

    after = bool(card.get("after_build"))
    actions = ([button("Adjust", "Adjust the plan"), button("Looks right", "Looks right", primary=True)] if after
               else [button("Adjust", "Adjust the plan"), button("Looks right, build it", "Looks right, build it", primary=True)])
    questions = [f'      <button type="button" data-send="{e(q, quote=True)}" style="font-size: 12px;">{e(q)} ↗</button>'
                 for q in card.get("questions", [])[:3]]

    page = TEMPLATE.read_text(encoding="utf-8")
    fills = {
        "sr_summary": "Confirmation of the planned dashboard: " + str(card["read"]),
        "heading": "Here's what I assumed" if after else "My read",
        "read": card["read"],
        "unsure": card.get("unsure") or "",
        "success": card.get("success_criteria") or "",
    }
    raw = {
        "chips": "\n".join(CHIP.format(e(c)) for c in chips),
        "wireframe": wireframe(goals, card.get("cadence")),
        "assumptions": "\n".join(rows),
        "questions": "\n".join(questions),
        "actions": "\n".join(actions),
    }
    present = {"unsure": bool(fills["unsure"]), "success": bool(fills["success"]), "questions": bool(questions)}
    page = re.sub(r"<!--section:(\w+)-->\n(.*?)<!--/section-->\n",
                  lambda m: m.group(2) if present.get(m.group(1)) else "", page, flags=re.DOTALL)
    for k, v in fills.items():
        page = page.replace("{{" + k + "}}", e(str(v)))
    for k, v in raw.items():
        page = page.replace("{{" + k + "}}", v)
    if "{{" in page or "<!--" in page:
        sys.exit("Template problem: unfilled placeholder or marker in assets/confirmation-card.html")
    sys.stdout.reconfigure(encoding="utf-8")
    print(page)


if __name__ == "__main__":
    main()
