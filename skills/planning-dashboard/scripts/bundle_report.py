"""Bundle a built dashboard and its data into one self-contained report.html, for sharing without a server.

Usage: python scripts/bundle_report.py out/<name> [--max-mb 15]

Reads out/<name>/4-dashboard/index.html and the data files listed in plan.md's header, embeds each file as
base64 in a <script type="application/octet-stream" data-file="..."> tag, and writes out/<name>/5-handoff/report.html.
The page must load its tables with the loadTable() helper from references/mosaic-tech.md ("Load data"), which reads
an embedded file when present and fetches it over http otherwise. Libraries still come from their CDNs, so opening
the report needs an internet connection but no server: double-click it, attach it, or put it on any static host.
"""
import base64
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from plan_format import parse  # noqa: E402

# 15 MB keeps the report under common email attachment limits (20-25 MB, after the mail client's own encoding)
# and under the 16 MB page limit of claude.ai artifacts.
DEFAULT_MAX_MB = 15


def die(msg):
    print(f"bundle_report: {msg}", file=sys.stderr)
    sys.exit(1)


def main(argv):
    if len(argv) < 2 or argv[1].startswith("-"):
        die("usage: python scripts/bundle_report.py out/<name> [--max-mb 15]")
    run = Path(argv[1])
    args = dict(zip(argv[2::2], argv[3::2]))
    try:
        max_mb = float(args.get("--max-mb", DEFAULT_MAX_MB))
    except ValueError:
        die(f"--max-mb must be a number, got {args['--max-mb']!r}")
    dash = run / "4-dashboard"
    page_path, plan_path = dash / "index.html", dash / "plan.md"
    for p in (page_path, plan_path):
        if not p.exists():
            die(f"missing {p}; build the page first (SKILL.md step 5)")
    page = page_path.read_text(encoding="utf-8")
    if "data-file" not in page:
        die("the page doesn't use the loadTable() helper (references/mosaic-tech.md, 'Load data'), "
            "so it can't read embedded data; switch its loading to loadTable() and run this again")
    plan, errors = parse(plan_path.read_text(encoding="utf-8"))
    files = [str(f["file"]) for f in plan.get("files", [])]
    if not files:
        die(f"plan.md lists no data files in its header ({'; '.join(errors) or 'data: is empty'})")
    tags = []
    for name in files:
        src = dash / name
        if not src.exists():
            die(f"plan.md lists {name}, but {src} doesn't exist; re-run the export in plan.md")
        data = base64.b64encode(src.read_bytes()).decode("ascii")
        tags.append(f'<script type="application/octet-stream" data-file="{name}">{data}</script>')
    # Module scripts run after the document is parsed, so data tags at the end of <body> are ready in time.
    if not re.search(r"</body>", page, flags=re.I):
        die("index.html has no </body> tag to put the data before")
    out = re.sub(r"</body>", "\n".join(tags) + "\n</body>", page, count=1, flags=re.I)
    dest = run / "5-handoff" / "report.html"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(out, encoding="utf-8")
    mb = dest.stat().st_size / 1e6
    print(f"Wrote {dest} ({mb:.1f} MB, {len(files)} data file(s) embedded)")
    if mb > max_mb:
        print(f"bundle_report: {mb:.1f} MB is over {max_mb:g} MB: export a smaller, pre-aggregated table "
              f"(references/destinations.md, 'Pre-aggregated exports') and bundle again", file=sys.stderr)
        sys.exit(2)


if __name__ == "__main__":
    main(sys.argv)
