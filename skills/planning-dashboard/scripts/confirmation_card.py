"""Print the confirmation card ("My read", assumptions, actions) from a small JSON file.

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
  "questions": ["Is there a target for the return rate?"]                (optional, at most 3)
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
CHIP = ('      <span style="font-size: 12px; padding: 3px 10px; border-radius: var(--radius); '
        'background: var(--bg-accent); color: var(--text-accent);">{}</span>')


def button(label, send, primary=False):
    style = ' style="background: var(--fill-primary); color: var(--on-primary); border: none;"' if primary else ""
    return f'    <button type="button" data-send="{e(send, quote=True)}"{style}>{e(label)} ↗</button>'


def order_goals(goals):
    """monitor always on top, present always at the bottom, the rest in the person's order."""
    middle = [g for g in goals if g not in ("monitor", "present")]
    return (["monitor"] if "monitor" in goals else []) + middle + (["present"] if "present" in goals else [])


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

    actions = [button("Adjust", "Adjust the plan"), button("Looks right, build it", "Looks right, build it", primary=True)]
    questions = [f'      <button type="button" data-send="{e(q, quote=True)}" style="font-size: 12px;">{e(q)} ↗</button>'
                 for q in card.get("questions", [])[:3]]

    page = TEMPLATE.read_text(encoding="utf-8")
    fills = {
        "sr_summary": "Confirmation of the planned dashboard: " + str(card["read"]),
        "heading": "My read",
        "read": card["read"],
        "unsure": card.get("unsure") or "",
        "success": card.get("success_criteria") or "",
    }
    raw = {
        "chips": "\n".join(CHIP.format(e(c)) for c in chips),
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
