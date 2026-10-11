"""Create a dashboard run folder with one numbered folder per step, or write its summary.

Usage:
  python run_folder.py init <out/name>      create the step folders and start the clock (run this first)
  python run_folder.py summary <out/name>   write README.md: each step's status, files, and timing

A step counts as done when its folder holds at least one file. The summary reads each
file's first heading or first line, so give every Markdown file a heading.

Timing comes from when files were saved, so measuring adds no tool calls. Two waits for the
person are measured separately and never count against a step:
  form shown (2-intake/form.html saved)  ->  answers in (2-intake/intake.md saved)
  card shown (5-confirm/card.html saved) ->  card answered (5-confirm/changes.md saved)
So save form.html and card.html right before showing them, and write intake.md and
changes.md first thing when the answer arrives. Budgets come from guidelines/timing.md.
"""
import re
import sys
import time
from pathlib import Path

TIMING_MD = Path(__file__).resolve().parent.parent / "guidelines" / "timing.md"
START = ".run-started"
WAITS = [("2-intake/form.html", "2-intake/intake.md", "filling in the form"),
         ("5-confirm/card.html", "5-confirm/changes.md", "reading the confirmation card")]

STEPS = [
    ("1-profile", "Profile", "quick look at the data, the full profile, and the observations drawn from it"),
    ("2-intake", "Intake", "the form built from the data, what was inferred, the answers"),
    ("3-data-check", "Data check", "questions asked about the data, answers, decisions"),
    ("4-layout", "Layout and story", "page blocks, finding-titles, and the query behind every number"),
    ("5-confirm", "Confirmation card", "card.json, the rendered card, and any changes made"),
    ("6-dashboard", "Plan and dashboard", "plan.md, its data files, validation result, and the built page"),
    ("7-handoff", "Hand-off", "which executor built it, the command, how to open it"),
    ("8-review", "Review", "checks run on the page, success criteria, next steps"),
]


def first_line(path):
    """A file's first heading or first line, skipping a YAML header. JSON files get no note."""
    if path.suffix not in (".md", ".txt"):
        return ""
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeDecodeError):
        return ""
    if lines and lines[0].strip() == "---":
        end = next((i for i, l in enumerate(lines[1:], 1) if l.strip() == "---"), 0)
        lines = lines[end + 1:]
    for line in lines:
        line = line.strip().lstrip("#").strip()
        if line and not line.startswith(">"):
            return line[:90]
    return ""


def budgets():
    """{folder: (target_upper, max)} from the table in guidelines/timing.md."""
    out = {}
    if not TIMING_MD.exists():
        return out
    for line in TIMING_MD.read_text(encoding="utf-8").splitlines():
        cells = [c.strip() for c in line.strip().strip("|").split("|")]
        if len(cells) >= 5 and re.fullmatch(r"`[\w-]+`", cells[1]):
            nums = [float(n) for n in re.findall(r"\d+(?:\.\d+)?", cells[3])]
            mx = re.findall(r"\d+(?:\.\d+)?", cells[4])
            if nums and mx:
                out[cells[1].strip("`")] = (max(nums), float(mx[0]))
    return out


def fmt(sec):
    return f"{sec:.1f} s" if sec < 90 else f"{sec / 60:.1f} min"


def timing(root):
    """Visible system time per step, from file save times, with the person's waits taken out."""
    start_file = root / START
    if not start_file.exists():
        return ["", "## Timing", "", "No timing: the run folder wasn't created with `init` at the start."]
    t0 = float(start_file.read_text(encoding="utf-8").strip())
    # The built page lives next to the plan, but building it is the hand-off's work.
    saves = sorted((p.stat().st_mtime, "7-handoff" if p.name == "index.html" else p.relative_to(root).parts[0], p)
                   for folder, _, _ in STEPS for p in (root / folder).glob("**/*") if p.is_file())
    if not saves:
        return []
    waits = []
    for a, b, why in WAITS:
        pa, pb = root / a, root / b
        if pa.exists() and pb.exists() and pb.stat().st_mtime > pa.stat().st_mtime:
            waits.append((pa.stat().st_mtime, pb.stat().st_mtime, why))
    per_step = {folder: 0.0 for folder, _, _ in STEPS}
    prev = t0
    for t, folder, _ in saves:
        gap = max(0.0, t - prev)
        hidden = sum(max(0.0, min(t, w1) - max(prev, w0)) for w0, w1, _ in waits)
        per_step[folder] += max(0.0, gap - hidden)
        prev = max(prev, t)
    limits = budgets()
    rows = ["", "## Timing", "",
            "Visible system time per step (time the person spent answering is listed separately).", "",
            "| Step | Time | Target | Max | |", "|---|---|---|---|---|"]
    for folder, title, _ in STEPS:
        sec = per_step[folder]
        tgt, mx = limits.get(folder, (None, None))
        mark = "" if tgt is None else ("within target" if sec <= tgt else "over target" if sec <= mx else "**over max**")
        rows.append(f"| {folder} {title} | {fmt(sec)} | {'' if tgt is None else f'≤ {tgt:g} s'} | "
                    f"{'' if mx is None else f'{mx:g} s'} | {mark} |")
    page = root / "6-dashboard" / "index.html"
    waited = sum(w1 - w0 for w0, w1, _ in waits)
    if page.exists():
        first = page.stat().st_mtime - t0 - sum(max(0.0, min(page.stat().st_mtime, w1) - w0) for w0, w1, _ in waits)
        rows += ["", f"**Time to first dashboard:** {fmt(max(0.0, first))} of system time "
                     f"({fmt(page.stat().st_mtime - t0)} wall clock)."]
    for w0, w1, why in waits:
        rows.append(f"- Waiting for the person {why}: {fmt(w1 - w0)}")
    if not waits:
        rows.append("- No waits for the person recorded.")
    rows.append(f"- Total system time: {fmt(sum(per_step.values()))}; total waiting: {fmt(waited)}.")
    return rows


def main():
    if len(sys.argv) != 3 or sys.argv[1] not in ("init", "summary"):
        sys.exit(__doc__)
    root = Path(sys.argv[2]).resolve()
    if sys.argv[1] == "init":
        for folder, _, _ in STEPS:
            (root / folder).mkdir(parents=True, exist_ok=True)
        if not (root / START).exists():
            (root / START).write_text(str(time.time()), encoding="utf-8")
        print(f"Created {len(STEPS)} step folders in {root}")
        return
    if not root.exists():
        sys.exit(f"{root} doesn't exist; run init first")
    lines = [f"# Dashboard run: {root.name}", "",
             "One folder per planning step. Open `6-dashboard/` for the result.", "",
             "| Step | Status | What's in it |", "|---|---|---|"]
    details = []
    for folder, title, purpose in STEPS:
        files = sorted(p for p in (root / folder).glob("**/*") if p.is_file()) if (root / folder).exists() else []
        status = "done" if files else "skipped"
        lines.append(f"| [{folder}]({folder}/) {title} | {status} | {purpose} |")
        if files:
            details.append(f"\n## {folder}: {title}\n")
            for p in files:
                rel = p.relative_to(root).as_posix()
                note = first_line(p)
                details.append(f"- [{p.relative_to(root / folder).as_posix()}]({rel})" + (f": {note}" if note else ""))
    (root / "README.md").write_text("\n".join(lines + timing(root) + details) + "\n", encoding="utf-8")
    print(f"Wrote {root / 'README.md'}")


if __name__ == "__main__":
    main()
