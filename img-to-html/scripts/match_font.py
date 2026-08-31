#!/usr/bin/env python3
"""Match a glyph crop against local fonts via render IoU. Used by img-to-html typography role."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    from PIL import Image, ImageDraw, ImageFont, ImageOps
except ImportError:
    print("Pillow required: pip install pillow", file=sys.stderr)
    sys.exit(1)


def _list_font_files() -> list[Path]:
    roots = [
        Path("/System/Library/Fonts"),
        Path("/Library/Fonts"),
        Path.home() / "Library/Fonts",
        Path("/usr/share/fonts"),
        Path.home() / ".local/share/fonts",
    ]
    exts = {".ttf", ".otf", ".ttc"}
    out: list[Path] = []
    for root in roots:
        if not root.is_dir():
            continue
        for p in root.rglob("*"):
            if p.suffix.lower() in exts:
                out.append(p)
    return out


def _binarize(im: Image.Image, size: tuple[int, int] = (128, 128)) -> Image.Image:
    g = ImageOps.grayscale(im).resize(size, Image.Resampling.LANCZOS)
    # ink = darker than mid after autocontrast
    g = ImageOps.autocontrast(g)
    return g.point(lambda x: 0 if x < 128 else 255, mode="1")


def _render_glyph(font_path: Path, text: str, size: tuple[int, int] = (128, 128)) -> Image.Image | None:
    try:
        font = ImageFont.truetype(str(font_path), size=96)
    except OSError:
        return None
    canvas = Image.new("L", (256, 256), 255)
    draw = ImageDraw.Draw(canvas)
    draw.text((16, 16), text, font=font, fill=0)
    bbox = canvas.getbbox()
    if not bbox:
        return None
    cropped = canvas.crop(bbox)
    return _binarize(cropped, size)


def _iou(a: Image.Image, b: Image.Image) -> float:
    pa, pb = list(a.getdata()), list(b.getdata())
    inter = sum(1 for x, y in zip(pa, pb) if x == 0 and y == 0)
    union = sum(1 for x, y in zip(pa, pb) if x == 0 or y == 0)
    return inter / union if union else 0.0


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--glyph", required=True, help="Path to glyph/word crop image")
    ap.add_argument("--text", required=True, help="Same characters as in the crop")
    ap.add_argument("--top", type=int, default=5)
    ap.add_argument("--limit-fonts", type=int, default=120, help="Max fonts to probe (keep low for speed)")
    args = ap.parse_args()

    target = _binarize(Image.open(args.glyph))
    fonts = _list_font_files()[: args.limit_fonts]
    scored: list[dict] = []
    for fp in fonts:
        rendered = _render_glyph(fp, args.text)
        if rendered is None:
            continue
        score = _iou(target, rendered)
        scored.append({"path": str(fp), "family": fp.stem, "score": round(score, 4)})

    scored.sort(key=lambda d: d["score"], reverse=True)
    top = scored[: args.top]
    print(json.dumps({"text": args.text, "matches": top}, indent=2))


if __name__ == "__main__":
    main()
