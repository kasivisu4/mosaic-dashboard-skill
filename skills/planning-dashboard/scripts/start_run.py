"""Do the whole first turn in one command: look at the data, start the full profile, print a form fitted to the data.

Usage: python start_run.py <out/name> <data file> [--skip field,field] [--glossary]
                           [--hint "field=text"]... [--columns col,col]

1. Creates the step folders and starts the run clock (as `run_folder.py init`).
2. Takes a quick look at the data (column types on a sample: well under a second for
   millions of rows, about 2 s for billions) and saves it to 1-profile/quick-look.json.
3. Starts the full `profile.py` in the background, writing 1-profile/profile.txt.
4. Builds the form: "What's the ask?" offers 2-3 asks this data can answer, and example text and
   goal subtitles use the data's own columns. Saves it to 2-intake/form.html
   and prints it, ready to pass unchanged to the inline widget.
   Exit code 2 (nothing printed) means every field is answered: skip the form.

--skip, --glossary, --hint as in intake_form.py; --columns as in profile.py.
"""
import json
import os
import subprocess
import sys
import time
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
from intake_form import build, parse_args  # noqa: E402
from quick_look import look as quick_look  # noqa: E402
from run_folder import START, STEPS  # noqa: E402


def start_profile(data, columns, out_file):
    """Run profile.py detached, so it keeps going after this command returns."""
    cmd = [sys.executable, str(HERE / "profile.py"), data] + (["--columns", columns] if columns else [])
    kwargs = {"stdout": open(out_file, "w", encoding="utf-8"), "stderr": subprocess.STDOUT, "stdin": subprocess.DEVNULL}
    if sys.platform == "win32":
        kwargs["creationflags"] = subprocess.DETACHED_PROCESS | subprocess.CREATE_NEW_PROCESS_GROUP
    else:
        kwargs["start_new_session"] = True
    subprocess.Popen(cmd, env={**os.environ, "PYTHONIOENCODING": "utf-8"}, **kwargs)


def main():
    args = sys.argv[1:]
    if len(args) < 2 or args[0] in ("-h", "--help"):
        sys.exit(__doc__)
    root, data = Path(args[0]), args[1]
    if not Path(data).exists():
        sys.exit(f"Data file not found: {data}")
    rest = args[2:]
    if "--columns" in rest:  # profile.py's option, not the form's
        i = rest.index("--columns")
        rest = rest[:i] + rest[i + 2:]
    skip, hints, _ = parse_args(rest)
    columns = None
    if "--columns" in args:
        i = args.index("--columns")
        columns = args[i + 1] if i + 1 < len(args) else sys.exit("--columns needs a comma-separated list")

    for folder, _, _ in STEPS:
        (root / folder).mkdir(parents=True, exist_ok=True)
    if not (root / START).exists():
        (root / START).write_text(str(time.time()), encoding="utf-8")

    try:
        look = quick_look(data)
    except Exception as err:  # an unreadable file shouldn't block the form; the full profile will report it
        print(f"note: quick look failed ({str(err).splitlines()[0]}); using the generic form", file=sys.stderr)
        look = None
    if look:
        (root / "1-profile" / "quick-look.json").write_text(json.dumps(look, indent=2), encoding="utf-8")
    start_profile(data, columns, root / "1-profile" / "profile.txt")

    page = build(skip, hints, look)
    if page is None:
        print("Nothing left to ask: every field is answered. Skip the form.", file=sys.stderr)
        sys.exit(2)
    (root / "2-intake" / "form.html").write_text(page, encoding="utf-8")
    sys.stdout.reconfigure(encoding="utf-8")
    print(page)


if __name__ == "__main__":
    main()
