#!/usr/bin/env python3
"""Recolor the WakaTime LOC chart (assets/bar_graph.png) for dark themes.

The waka-readme-stats action renders this chart with a white matplotlib
canvas every day. We invert ONLY neutral pixels (white bg -> dark,
black text/axes -> white/light) while leaving saturated language-color
bars untouched. Runs right after the waka workflow via workflow_run.
Idempotent: skips if the chart is already dark."""

import sys
from pathlib import Path

from PIL import Image, ImageChops, ImageOps

CHART = Path(__file__).resolve().parents[2] / "assets" / "bar_graph.png"
DARK_BG = (13, 17, 23)          # github dark #0d1117
NEUTRAL_THRESHOLD = 30          # max(R,G,B)-min(R,G,B) below this = grayscale-ish


def main() -> None:
    if not CHART.exists():
        print("chart not found; skipping")
        sys.exit(0)

    img = Image.open(CHART).convert("RGB")

    # idempotency: top-left corner pixel is page background
    corner = img.getpixel((10, 10))
    if sum(corner[:3]) < 250:
        print("chart already dark; nothing to do")
        return

    r, g, b = img.split()
    mx = ImageChops.lighter(ImageChops.lighter(r, g), b)
    mn = ImageChops.darker(ImageChops.darker(r, g), b)
    chroma = ImageChops.subtract(mx, mn)

    # mask: white where pixel is neutral (text/bg/grid), black where colored
    mask = chroma.point(lambda p: 255 if p < NEUTRAL_THRESHOLD else 0)

    inverted = ImageOps.invert(img)
    out = Image.composite(inverted, img, mask.convert("L"))

    # blend pure-inverted whites down to github-dark instead of harsh black
    overlay = Image.new("RGB", out.size, DARK_BG)
    gray_out = out.convert("L")
    soft = Image.composite(overlay, out, gray_out.point(lambda p: 255 if p > 245 else 0))

    soft.save(CHART)
    print(f"darkened {CHART.name} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
