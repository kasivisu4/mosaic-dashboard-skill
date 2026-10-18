"""Record what a dashboard run cost: model, tokens, estimated price, and the skill version that built it.

Usage: python scripts/record_usage.py out/<name> --model MODEL_ID --tokens TOTAL [--input N --output N --cache-read N] [--note TEXT]

Writes out/<name>/5-handoff/usage.json. Whoever ran the build (the person, or the agent that orchestrated it)
reports the tokens: agent runs usually report one total, so the price is estimated from a typical agentic token
mix and shown with a low-high range. Pass --input/--output/--cache-read when the split is known for an exact figure.
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
    args = dict(zip(argv[2::2], argv[3::2]))
    model = args.get("--model")
    if model not in PRICES:
        die(f"--model must be one of {', '.join(PRICES)}; got {model!r} (add its prices to PRICES with their date)")
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
    dest = run / "5-handoff" / "usage.json"
    dest.parent.mkdir(parents=True, exist_ok=True)
    dest.write_text(json.dumps(out, indent=2), encoding="utf-8")
    rng = f" (range ${out['cost_range_usd'][0]}–${out['cost_range_usd'][1]})" if "cost_range_usd" in out else ""
    print(f"{run.name}: {out['tokens']:,} tokens on {model}, about ${out['cost_usd']}{rng}; skill {out['skill_version']}")


if __name__ == "__main__":
    main(sys.argv)
