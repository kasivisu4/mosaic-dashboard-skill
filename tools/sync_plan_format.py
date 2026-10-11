"""Copy the plan-format parser from the planner to every executor skill, so both read plans the same way.

Usage (from the repo root): python tools/sync_plan_format.py [--check]
--check exits 1 if any copy differs, without writing.
"""
import sys
from pathlib import Path

root = Path(__file__).resolve().parent.parent
source = root / "skills" / "planning-dashboard" / "scripts" / "plan_format.py"
check = "--check" in sys.argv
stale = []
for target in sorted(root.glob("skills/*/scripts/plan_format.py")):
    if target == source:
        continue
    if target.read_bytes() != source.read_bytes():
        stale.append(target)
        if not check:
            target.write_bytes(source.read_bytes())
for t in stale:
    print(("differs: " if check else "updated: ") + str(t.relative_to(root)))
if not stale:
    print("all plan_format.py copies match")
sys.exit(1 if check and stale else 0)
