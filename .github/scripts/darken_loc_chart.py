#!/usr/bin/env python3
"""Recolor the WakaTime LOC chart (assets/bar_graph.png) for dark themes.

The waka-readme-stats action renders this chart with a white matplotlib
canvas daily. We gamma-correct-invert ONLY neutral pixels so text stays
crisp, blend the background into github-dark (#0d1117), and leave the
saturated language-color bars untouched. Idempotent."""

import sys
from pathlib import Path

from PIL import Image, ImageChops

CHART = Path(__file__).resolve().parents[2] / "assets" / "bar_graph.png"
DARK_BG = (13, 17, 23)      # github dark #0d1117
GAMMA = 1.9                 # >1 keeps antialiased strokes thin & crisp on dark
NEUTRAL_THRESHOLD = 30      # max(R,G,B)-min(R,G,B) below this = grayscale-ish


def build_lut(dark_channel: int) -> list[int]:
    """Map source channel value -> inverted value anchored at DARK_BG.
    v=255 (white bg) -> dark_channel ; v=0 (black text) -> 255."""
    span = 255 - dark_channel
    lut = []
    for v in range(256):
        x = 1.0 - v / 255.0
        val = dark_channel + span * (x**GAMMA)
        lut.append(max(0, min(255, round(val))))
    return lut


def main() -> None:
    if not CHART.exists():
        print("chart not found; skipping")
        sys.exit(0)

    img = Image.open(CHART).convert("RGB")

    corner = img.getpixel((10, 10))
    if sum(corner[:3]) < 250:
        print("chart already dark; nothing to do")
        return

    r, g, b = img.split()
    mx = ImageChops.lighter(ImageChops.lighter(r, g), b)
    mn = ImageChops.darker(ImageChops.darker(r, g), b)
    chroma = ImageChops.subtract(mx, mn)
    mask = chroma.point(lambda p: 255 if p < NEUTRAL_THRESHOLD else 0)  # white=neutral

    luts = [build_lut(c) for c in DARK_BG]
    transformed = img.point(luts[0] + luts[1] + luts[2])

    out = Image.composite(transformed, img, mask)
    out.save(CHART)
    print(f"darkened {CHART.name} ({img.size[0]}x{img.size[1]})")


if __name__ == "__main__":
    main()
