#!/usr/bin/env python3
"""Deterministic visual measurement for img-to-html.

Extracts canvas size, quantized palette, OCR strings + boxes, and coarse
region hints. No vision API.

Usage:
  uv run ~/.agents/skills/img-to-html/scripts/measure.py reference.png --out measure.json
"""

from __future__ import annotations

import argparse
import json
import shutil
import subprocess
import sys
from collections import Counter
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError as e:
    print("needs Pillow + numpy:", e, file=sys.stderr)
    sys.exit(2)


def hexify(rgb) -> str:
    r, g, b = (int(max(0, min(255, x))) for x in rgb)
    return f"#{r:02x}{g:02x}{b:02x}"


def quantize_palette(im: Image.Image, n: int = 12) -> list[dict]:
    """Median-cut palette with approximate pixel shares."""
    small = im.convert("RGB")
    # speed: shrink for counting
    w, h = small.size
    scale = max(1, int(max(w, h) / 640))
    if scale > 1:
        small = small.resize((w // scale, h // scale), Image.Resampling.BOX)
    q = small.quantize(colors=n, method=Image.Quantize.MEDIANCUT)
    palette = q.getpalette() or []
    colors = []
    for i in range(n):
        r, g, b = palette[i * 3 : i * 3 + 3]
        colors.append((r, g, b))
    counts = Counter(q.getdata())
    total = sum(counts.values()) or 1
    out = []
    for idx, cnt in counts.most_common(n):
        if idx >= len(colors):
            continue
        rgb = colors[idx]
        out.append(
            {
                "hex": hexify(rgb),
                "rgb": list(rgb),
                "share": round(cnt / total, 4),
            }
        )
    return out


def sample_corners_and_center(arr: np.ndarray) -> dict:
    h, w = arr.shape[:2]

    def patch(x, y, r=4):
        return hexify(arr[max(0, y - r) : y + r + 1, max(0, x - r) : x + r + 1].mean((0, 1)))

    return {
        "tl": patch(8, 8),
        "tr": patch(w - 9, 8),
        "bl": patch(8, h - 9),
        "br": patch(w - 9, h - 9),
        "center": patch(w // 2, h // 2),
    }


def run_tesseract(path: Path) -> list[dict]:
    if not shutil.which("tesseract"):
        return []
    # TSV: level page block par line word ... left top width height conf text
    try:
        proc = subprocess.run(
            ["tesseract", str(path), "stdout", "--psm", "6", "tsv"],
            capture_output=True,
            text=True,
            check=False,
            timeout=120,
        )
    except (subprocess.TimeoutExpired, OSError):
        return []
    lines = proc.stdout.splitlines()
    if len(lines) < 2:
        return []
    header = lines[0].split("\t")
    idx = {name: i for i, name in enumerate(header)}
    needed = ["level", "left", "top", "width", "height", "conf", "text"]
    if any(k not in idx for k in needed):
        return []
    words = []
    for row in lines[1:]:
        cols = row.split("\t")
        if len(cols) <= max(idx.values()):
            continue
        try:
            level = int(cols[idx["level"]])
            conf = float(cols[idx["conf"]])
        except ValueError:
            continue
        if level != 5 or conf < 40:  # word level
            continue
        text = cols[idx["text"]].strip()
        if not text:
            continue
        left = int(cols[idx["left"]])
        top = int(cols[idx["top"]])
        width = int(cols[idx["width"]])
        height = int(cols[idx["height"]])
        words.append(
            {
                "text": text,
                "box": [left, top, left + width, top + height],
                "conf": round(conf, 1),
                "height_px": height,
                # rough font-size estimate from glyph box
                "est_font_px": max(8, int(round(height * 0.85))),
            }
        )
    return words


def cluster_font_roles(words: list[dict]) -> dict:
    if not words:
        return {}
    heights = sorted(w["est_font_px"] for w in words)
    # simple terciles → display / body / caption
    n = len(heights)
    lo = heights[n // 3]
    hi = heights[(2 * n) // 3]
    return {
        "caption_px_hint": lo,
        "body_px_hint": heights[n // 2],
        "display_px_hint": hi,
        "min_px": heights[0],
        "max_px": heights[-1],
    }


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image", type=Path)
    ap.add_argument("--out", type=Path, required=True)
    ap.add_argument("--colors", type=int, default=12)
    args = ap.parse_args()

    im = Image.open(args.image).convert("RGB")
    w, h = im.size
    arr = np.asarray(im, dtype=np.float64)

    palette = quantize_palette(im, n=args.colors)
    samples = sample_corners_and_center(arr)
    ocr = run_tesseract(args.image)
    roles = cluster_font_roles(ocr)

    # page bg guess: most common dark-ish or top-share color near corners
    page_bg = samples["tl"]
    if palette:
        # prefer highest-share color
        page_bg = palette[0]["hex"]

    measure = {
        "source": str(args.image.resolve()),
        "canvas": {"width": w, "height": h},
        "page_bg_guess": page_bg,
        "corner_samples": samples,
        "palette": palette,
        "ocr": {
            "engine": "tesseract" if ocr else None,
            "word_count": len(ocr),
            "words": ocr[:400],  # cap payload
            "font_roles_hint": roles,
            "strings_joined": " ".join(w["text"] for w in ocr[:200]),
        },
    }

    args.out.parent.mkdir(parents=True, exist_ok=True)
    args.out.write_text(json.dumps(measure, indent=2), encoding="utf-8")
    print(
        json.dumps(
            {
                "out": str(args.out),
                "canvas": measure["canvas"],
                "palette_n": len(palette),
                "ocr_words": len(ocr),
                "page_bg_guess": page_bg,
            }
        )
    )


if __name__ == "__main__":
    main()
