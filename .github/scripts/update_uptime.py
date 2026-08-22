#!/usr/bin/env python3
"""Rewrite the `$ uptime --fun` line in README.md using numbers
scraped from the auto-generated WakaTime block. No extra API calls:
the waka-readme workflow refreshes those stats daily, and this runs
right after it via workflow_run."""

import re
import sys
from pathlib import Path

README = Path(__file__).resolve().parents[2] / "README.md"

HUMOR = "humor module: enabled"


def extract(readme: str) -> dict | None:
    start = readme.find("<!--START_SECTION:waka-->")
    end = readme.find("<!--END_SECTION:waka-->")
    if start == -1 or end == -1 or end <= start:
        print("waka markers not found", file=sys.stderr)
        return None

    block = readme[start:end]

    code_time = re.search(r"Code%20Time-(\d+)(?:%20hrs)?", block)
    loc = re.search(r"([\d.]+)(?:%20|\s)million%20lines", block)
    ai_pct = re.search(r"(\d+(?:\.\d+)?)%\s*(?:%20)?AI-written", block)

    if not (code_time and loc and ai_pct):
        missing = [n for n, m in [("code_time", code_time), ("loc", loc), ("ai_pct", ai_pct)] if not m]
        print(f"could not parse: {missing}", file=sys.stderr)
        return None

    return {
        "hrs": int(code_time.group(1)),
        "loc": loc.group(1),
        "pct": int(float(ai_pct.group(1))),
    }


def main() -> None:
    readme = README.read_text(encoding="utf-8")
    data = extract(readme)
    if data is None:
        sys.exit(0)  # never break the profile over a parse miss

    new_line = (
        f"{data['hrs']}+ hrs of code time \u00b7 {data['loc']}M lines written "
        f"\u00b7 {data['pct']}% AI co-authored \u00b7 {HUMOR}"
    )

    pattern = re.compile(
        r"(?m)^(\d+\+ hrs of code time \u00b7 \d+(?:\.\d+)?M lines written "
        r"\u00b7 \d+% AI co-authored \u00b7 )humor module: enabled$"
    )
    updated, n = pattern.subn(new_line.replace("\\", "\\\\"), readme)
    if n != 1:
        print("uptime section not found exactly once; skipping", file=sys.stderr)
        sys.exit(0)

    if updated != readme:
        README.write_text(updated, encoding="utf-8")
        print(f"updated -> {new_line}")
    else:
        print("uptime line already current")


if __name__ == "__main__":
    main()
