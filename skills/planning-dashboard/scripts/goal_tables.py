"""Read the label tables in guidelines/goals.md, so forms and cards use the organization's own wording.

Shared by intake_form.py and confirmation_card.py.
"""
import re
from pathlib import Path

GOALS_MD = Path(__file__).resolve().parent.parent / "guidelines" / "goals.md"
SECTIONS = ("Goals", "Page blocks per goal", "Page format", "Audiences", "Cadence", "Review depth")


def read_tables(path=GOALS_MD):
    """Return {section: [(id, [cells after id]), ...]} in table order. Raises SystemExit with a clear message."""
    if not path.exists():
        raise SystemExit(f"Missing {path}; the intake needs guidelines/goals.md")
    tables, current = {}, None
    for line in path.read_text(encoding="utf-8").splitlines():
        heading = re.match(r"^##\s+(.+?)\s*$", line)
        if heading:
            current = heading.group(1)
            continue
        row = re.match(r"^\|\s*`([\w-]+)`\s*\|(.*)\|\s*$", line)
        if row and current in SECTIONS:
            cells = [c.strip() for c in row.group(2).split("|")]
            tables.setdefault(current, []).append((row.group(1), cells))
    missing = [s for s in SECTIONS if not tables.get(s)]
    if missing:
        raise SystemExit(f"guidelines/goals.md is missing table rows under: {', '.join(missing)}")
    return tables


def goal_cards(tables, section="Goals"):
    """[(id, title, subtitle, icon)] from 'Title · "Subtitle" · `ti-icon`' (Goals, Page format)."""
    out = []
    for gid, cells in tables[section]:
        parts = [p.strip() for p in cells[0].split("·")]
        title = parts[0]
        subtitle = parts[1].strip('"“”') if len(parts) > 1 else ""
        icon = parts[2].strip("`") if len(parts) > 2 else "ti-chart-bar"
        out.append((gid, title, subtitle, icon))
    return out


def labels(tables, section):
    """{id: form label} for Audiences, Cadence, Review depth (label is the first cell)."""
    return {rid: cells[0] for rid, cells in tables[section]}
