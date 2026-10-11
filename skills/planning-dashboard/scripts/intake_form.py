"""Print the "Dashboard details" intake form, showing only the questions still unanswered.

Usage: python intake_form.py [--skip field,field] [--glossary] [--data FILE] [--hint "field=text"]...

Fields: goal, cadence, request, success_criteria, data, glossary, audience, review_depth.
--skip      drop questions already answered by the request or attachments
--glossary  include the glossary question (left out unless asked for; see guidelines/goals.md)
--data      take a quick look at the data file: "What's the ask?" offers 2-3 asks this data can
            answer, and example text and goal subtitles use its columns
--hint      replace a text box's example text, e.g. "success_criteria=e.g. I can spot a bad week"

Pass the printed HTML unchanged to the inline form widget (load its elicitation module first).
Option labels and icons come from guidelines/goals.md. Exit code 2 = nothing left to ask.
"""
import html
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from goal_tables import goal_cards, labels, read_tables  # noqa: E402

TEMPLATE = Path(__file__).resolve().parent.parent / "assets" / "intake-form.html"
FIELDS = ["goal", "cadence", "request", "success_criteria", "data", "glossary", "audience", "review_depth"]
CHOICE_FIELDS = ("goal", "cadence", "audience", "review_depth")
TEXT_FIELDS = ("request", "success_criteria", "data_text", "glossary")
DEFAULT_TEXT = {
    "request": "Your own words, or paste the Slack message or email you got",
    "success_criteria": "e.g. I can see the top 3 drivers of the drop in under 10 seconds",
    "data_text": "or describe where it lives",
    "glossary": "e.g. NPA = 90+ days past due; active = 1+ transaction in 30 days",
}
# Kept short on purpose: the form is passed through the model as text, so every character costs output time.
CARD_STYLE = ("border-radius:12px;padding:12px 14px;display:flex;gap:10px;align-items:flex-start;"
              "text-align:left;box-shadow:0 1px 2px rgba(0,0,0,.04)")
e = html.escape


def card(gid, title, subtitle, icon):
    return (f'<button type="button" class="elicit-pill" data-value="{e(gid)}" style="{CARD_STYLE}">'
            f'<i class="ti {e(icon)}" style="font-size:20px" aria-hidden="true"></i>'
            f'<span><span style="font-size:13px;font-weight:500">{e(title)}</span><br>'
            f'<span style="font-size:11px;color:var(--text-muted)">{e(subtitle)}</span></span></button>')


def pills(options):
    return "".join(f'<button type="button" class="elicit-pill" data-value="{e(k)}">{e(v)}</button>'
                   for k, v in options.items())


def ask_options(look):
    """2-3 questions this data can answer, built from its date, measure, flag and dimensions."""
    if not look:
        return []
    date, measure, flag, dims = look["date"], look["measure"], look["flag"], look["dims"]
    asks = []
    if flag and dims:
        asks.append(f"Which {dims[0]} has the highest % {flag}?")
    if date and measure and dims:
        asks.append(f"Why did {measure} change by {dims[0]} last month?")
    elif measure and len(dims) > 1:
        asks.append(f"How does {measure} compare across {dims[0]} and {dims[1]}?")
    if date and (flag or measure):
        asks.append(f"How has {'% ' + flag if flag else measure} moved over time?")
    elif measure and dims:
        asks.append(f"Which {dims[-1]} has the highest {measure}?")
    return list(dict.fromkeys(asks))[:3]


def data_text(look):
    """Example text and goal subtitles written with the data's own column names."""
    if not look:
        return {}, {}
    date, measure, flag, dims = look["date"], look["measure"], look["flag"], look["dims"]
    dim = dims[0] if dims else None
    metric = f"% {flag}" if flag else measure
    texts, subtitles = {}, {}
    if measure and dim:
        texts["request"] = "Or in your own words, or paste the Slack message or email you got"
        subtitles["answer"] = f"Why did {measure} change?" if date else f"Which {dim} leads on {measure}?"
        subtitles["explore"] = f"{measure} by {' and '.join(dims[:2])}"
    if metric and dim:
        texts["success_criteria"] = f"e.g. I can see which {dim} has the highest {metric} at a glance"
        if date:
            subtitles["monitor"] = f"Watch {metric} by {dim}"
    if measure:
        subtitles["present"] = f"Tell the story of {measure}"
    return texts, subtitles


def parse_args(args):
    """Return (skip, hints, data_file). Exits with a clear message on bad input."""
    known = {"--skip", "--glossary", "--data", "--hint"}
    flags = [a for i, a in enumerate(args) if a.startswith("--") and not (i and args[i - 1] in ("--hint",))]
    unknown_flags = [a for a in flags if a not in known]
    if unknown_flags:
        sys.exit(f"Unknown option(s): {', '.join(unknown_flags)}. Options: {', '.join(sorted(known))}")

    def value(flag):
        i = args.index(flag)
        if i + 1 >= len(args):
            sys.exit(f"{flag} needs a value")
        return args[i + 1]

    skip = {s.strip() for s in value("--skip").split(",") if s.strip()} if "--skip" in args else set()
    unknown = skip - set(FIELDS)
    if unknown:
        sys.exit(f"Unknown field(s) for --skip: {', '.join(sorted(unknown))}. Fields: {', '.join(FIELDS)}")
    if "--glossary" not in args:
        skip.add("glossary")


    hints = {}
    for i, a in enumerate(args):
        if a == "--hint" and i + 1 < len(args):
            field, _, text = args[i + 1].partition("=")
            if field.strip() not in TEXT_FIELDS:
                sys.exit(f"--hint field '{field}' must be one of {', '.join(TEXT_FIELDS)}")
            hints[field.strip()] = text.strip()
    data_file = value("--data") if "--data" in args else None
    return skip, hints, data_file


def build(skip, hints=None, look=None):
    """The form HTML with only the fields not in skip, or None when nothing is left to ask."""
    keep = [f for f in FIELDS if f not in skip]
    if not keep:
        return None
    hints = hints or {}
    tables = read_tables()

    texts, subtitles = data_text(look)
    page = TEMPLATE.read_text(encoding="utf-8")
    page = page.replace("{{goal_cards}}", "".join(
        card(gid, title, subtitles.get(gid, sub), icon)
        for gid, title, sub, icon in goal_cards(tables)))
    page = page.replace("{{cadence_pills}}", pills(labels(tables, "Cadence")))
    page = page.replace("{{audience_pills}}", pills(labels(tables, "Audiences")))
    page = page.replace("{{review_depth_pills}}", pills(labels(tables, "Review depth")))
    asks = ask_options(look)
    page = page.replace("{{ask_label}}", "What's the ask? Pick one, or paste the original request if you have it."
                        if asks else "What's the ask? Paste the original request if you have it.")
    page = page.replace("{{ask_pills}}", (
        '<div class="elicit-pills" data-name="suggested_ask" data-multi="false">'
        + "".join(f'<button type="button" class="elicit-pill" data-value="{e(a, quote=True)}">{e(a)}</button>' for a in asks)
        + "</div>") if asks else "")
    for field in TEXT_FIELDS:
        page = page.replace("{{ph_" + field + "}}", e(hints.get(field) or texts.get(field) or DEFAULT_TEXT[field], quote=True))

    def group(m):
        return m.group(2).rstrip() + "\n" if m.group(1) in keep else ""

    page = re.sub(r"<!--group:(\w+)-->\n(.*?)<!--/group-->\n", group, page, flags=re.DOTALL)
    page = re.sub(r">\s+<", "><", page).strip()  # whitespace between tags has no layout meaning here
    if "<!--" in page or "{{" in page:
        sys.exit("Template problem: unmatched group markers or placeholders in assets/intake-form.html")
    return page


def main():
    args = sys.argv[1:]
    if "-h" in args or "--help" in args:
        sys.exit(__doc__)
    skip, hints, data_file = parse_args(args)
    look = None
    if data_file:
        from quick_look import look as quick_look
        look = quick_look(data_file)
    page = build(skip, hints, look)
    if page is None:
        print("Nothing left to ask: every field is answered. Skip the form.", file=sys.stderr)
        sys.exit(2)
    sys.stdout.reconfigure(encoding="utf-8")
    print(page)


if __name__ == "__main__":
    main()
