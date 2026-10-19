"""Record what a dashboard run cost: model, tokens, estimated price, and the skill version that built it.

Usage: python scripts/record_usage.py out/<name> --transcript FILE.jsonl [FILE.jsonl ...] [--note TEXT]
       python scripts/record_usage.py out/<name> --model MODEL_ID --tokens TOTAL|unknown [--note TEXT]

Writes out/<name>/5-handoff/usage.json. The exact way: point it at the run's Claude Code transcript(s)
(~/.claude/projects/<project folder>/<session>.jsonl, and <session>/subagents/agent-*.jsonl for agents); it sums
every model call's input, output, cache-read and cache-write tokens and prices them. Without a transcript, a
reported total is priced from a typical agentic mix with a wide range, or recorded as unknown.
"""
import json
import re
import sys
from datetime import date
from pathlib import Path

SKILL_MD = Path(__file__).resolve().parent.parent / "SKILL.md"
# USD per million tokens: input, output, cache read. Anthropic first-party API prices as of 2026-10-06.
# Haiku 5.5's cache-read price isn't listed there; 10% of input is assumed (the usual cache-read ratio).
PRICES_AS_OF = "2026-10-06"
PRICES = {
    "claude-opus-5-5": (4.00, 20.00, 0.20),
    "claude-sonnet-5-5": (2.00, 10.00, 0.20),
    "claude-haiku-5-5": (0.10, 0.50, 0.01),
    "claude-fable-5-1": (10.00, 50.00, 0.25),
}
# Cache writes aren't in the price table above: priced at the standard 1.25x input for 5-minute writes, with
# 2x input (1-hour writes) as the top of the range.
CACHE_WRITE_MULT, CACHE_WRITE_MULT_1H = 1.25, 2.0
# Typical mix of a long agentic build loop, where the context is resent (and mostly cached) every turn:
# most tokens are cache reads, a few are fresh input, a small share is output. Low and high bounds bracket it.
MIX = {"likely": (0.06, 0.04, 0.90), "low": (0.02, 0.02, 0.96), "high": (0.20, 0.08, 0.72)}


def die(msg):
    print(f"record_usage: {msg}", file=sys.stderr)
    sys.exit(1)


def skill_version():
    m = re.search(r"^\s+version:\s*\"?([\w.\-]+)\"?\s*$", SKILL_MD.read_text(encoding="utf-8"), flags=re.M)
    return m.group(1) if m else "unversioned"


def cost(prices, inp, out, cache):
    return round((inp * prices[0] + out * prices[1] + cache * prices[2]) / 1e6, 2)


def main(argv):
    if len(argv) < 2 or argv[1].startswith("-"):
        die("usage: python scripts/record_usage.py out/<name> --model MODEL_ID --tokens TOTAL [--input N --output N --cache-read N]")
    run = Path(argv[1])
    if not run.is_dir():
        die(f"{run} is not a run folder")
    if "--transcript" in argv:
        return from_transcripts(run, argv)
    args = dict(zip(argv[2::2], argv[3::2]))
    model = args.get("--model")
    if model not in PRICES:
        die(f"--model must be one of {', '.join(PRICES)}; got {model!r} (add its prices to PRICES with their date)")
    if args.get("--tokens") == "unknown":
        out = {"model": model, "skill_version": skill_version(), "recorded": date.today().isoformat(), "tokens": None, "cost_usd": None,
               "note": args.get("--note", "Token count unknown: the run's transcript wasn't available.")}
        return write(run, out)
    try:
        nums = {k: int(args[k].replace(",", "")) for k in ("--tokens", "--input", "--output", "--cache-read") if k in args}
    except ValueError as e:
        die(f"token counts must be whole numbers: {e}")
    p = PRICES[model]
    out = {"model": model, "skill_version": skill_version(), "recorded": date.today().isoformat(),
           "prices_usd_per_mtok": {"input": p[0], "output": p[1], "cache_read": p[2], "as_of": PRICES_AS_OF}}
    if all(k in nums for k in ("--input", "--output", "--cache-read")):
        i, o, c = nums["--input"], nums["--output"], nums["--cache-read"]
        out.update(tokens=i + o + c, split={"input": i, "output": o, "cache_read": c}, cost_usd=cost(p, i, o, c), cost_basis="exact split")
    elif "--tokens" in nums:
        t = nums["--tokens"]
        est = {k: cost(p, t * a, t * b, t * c) for k, (a, b, c) in MIX.items()}
        out.update(tokens=t, cost_usd=est["likely"], cost_range_usd=[est["low"], est["high"]],
                   cost_basis="estimated from a typical agentic mix (input/output/cache-read) " + "/".join(f"{x:.0%}" for x in MIX["likely"]))
    else:
        die("give --tokens TOTAL, or all of --input, --output and --cache-read")
    if "--note" in args:
        out["note"] = args["--note"]
    write(run, out)


def write(run, out):
    dest = run / "5-handoff" / "usage.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    if out.get("tokens") is None:
        print(f"{run.name}: tokens unknown on {out['model']}; skill {out['skill_version']}")
        return
    rng = f" (range ${out['cost_range_usd'][0]}–${out['cost_range_usd'][1]})" if "cost_range_usd" in out else ""
    print(f"{run.name}: {out['tokens']:,} tokens on {out['model']}, about ${out['cost_usd']}{rng}; skill {out['skill_version']}")


def from_transcripts(run, argv):
    """Exact usage from Claude Code transcript files: one usage block per model call (deduplicated by message id)."""
    i = argv.index("--transcript")
    files = []
    for a in argv[i + 1:]:   # the files run up to the next flag
        if a.startswith("--"):
            break
        files.append(a)
    note = argv[argv.index("--note") + 1] if "--note" in argv else None
    if not files:
        die("--transcript needs one or more .jsonl files")
    # A streamed reply is logged in pieces that share one message id; the last piece carries the final counts.
    # Keep, per call, the largest value of each count.
    per_call, models = {}, {}
    keys = {"input": "input_tokens", "output": "output_tokens", "cache_read": "cache_read_input_tokens", "cache_write": "cache_creation_input_tokens"}
    for f in files:
        path = Path(f)
        if not path.exists():
            die(f"transcript not found: {path}")
        for n, line in enumerate(path.read_text(encoding="utf-8", errors="replace").splitlines()):
            try:
                msg = json.loads(line).get("message") or {}
            except json.JSONDecodeError:
                continue
            u = msg.get("usage")
            if not u:
                continue
            mid = msg.get("id") or f"{path.name}:{n}"
            if mid not in per_call:
                models[msg.get("model")] = models.get(msg.get("model"), 0) + 1
            cur = per_call.setdefault(mid, {k: 0 for k in keys})
            for k, field in keys.items():
                cur[k] = max(cur[k], u.get(field) or 0)
    calls = len(per_call)
    sums = {k: sum(c[k] for c in per_call.values()) for k in keys}
    if not calls:
        die("no model calls with usage found in the transcript(s)")
    model = max(models, key=models.get)
    if model not in PRICES:
        die(f"transcript's main model {model!r} has no prices in PRICES; add it with its date")
    p = PRICES[model]
    base = (sums["input"] * p[0] + sums["output"] * p[1] + sums["cache_read"] * p[2]) / 1e6
    low, high = base + sums["cache_write"] * p[0] * CACHE_WRITE_MULT / 1e6, base + sums["cache_write"] * p[0] * CACHE_WRITE_MULT_1H / 1e6
    out = {"model": model, "models": models, "skill_version": skill_version(), "recorded": date.today().isoformat(),
           "calls": calls, "tokens": sum(sums.values()), "split": sums, "cost_usd": round(low, 2), "cost_range_usd": [round(low, 2), round(high, 2)],
           "cost_basis": "exact token split from the transcript; cache writes at 1.25x input (2x for 1-hour writes, the range's top)",
           "prices_usd_per_mtok": {"input": p[0], "output": p[1], "cache_read": p[2], "as_of": PRICES_AS_OF},
           "transcripts": [Path(f).name for f in files]}
    if note:
        out["note"] = note
    write(run, out)


if __name__ == "__main__":
    main(sys.argv)
