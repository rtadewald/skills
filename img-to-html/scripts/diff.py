#!/usr/bin/env python3
"""Pixel diff reference vs render. Writes score, heatmap mask, and worst-region crop.

No skimage dependency — MAE + tiled search.

Usage:
  uv run ~/.agents/skills/img-to-html/scripts/diff.py \\
    --ref reference.png --render review/render.png --outdir review/diff-1
"""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError as e:
    print("needs Pillow + numpy:", e, file=sys.stderr)
    sys.exit(2)


def load_rgb(path: Path, size: tuple[int, int] | None = None) -> np.ndarray:
    im = Image.open(path).convert("RGB")
    if size and im.size != size:
        im = im.resize(size, Image.Resampling.LANCZOS)
    return np.asarray(im, dtype=np.float32)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--ref", type=Path, required=True)
    ap.add_argument("--render", type=Path, required=True)
    ap.add_argument("--outdir", type=Path, required=True)
    ap.add_argument("--tile", type=int, default=64, help="tile size for worst-region search")
    ap.add_argument("--pad", type=int, default=24, help="padding around worst tile for crop")
    ap.add_argument("--threshold", type=float, default=28.0, help="per-channel MAE threshold for mask")
    args = ap.parse_args()

    ref_im = Image.open(args.ref).convert("RGB")
    w, h = ref_im.size
    ref = np.asarray(ref_im, dtype=np.float32)
    rend = load_rgb(args.render, size=(w, h))

    diff = np.abs(ref - rend)
    mae = float(diff.mean())
    # rough similarity 0–1 (1 = identical)
    score = max(0.0, 1.0 - mae / 255.0)

    # binary-ish mask (max channel error)
    err = diff.max(axis=2)
    mask = (err >= args.threshold).astype(np.uint8) * 255
    heat = np.clip(err / max(err.max(), 1.0) * 255, 0, 255).astype(np.uint8)

    # tiled MAE — find worst tile
    tw = max(16, args.tile)
    best = (-1.0, 0, 0)  # mae, x, y
    for y in range(0, h - tw + 1, tw // 2 or tw):
        for x in range(0, w - tw + 1, tw // 2 or tw):
            tile_mae = float(diff[y : y + tw, x : x + tw].mean())
            if tile_mae > best[0]:
                best = (tile_mae, x, y)
    _, bx, by = best
    pad = args.pad
    x0 = max(0, bx - pad)
    y0 = max(0, by - pad)
    x1 = min(w, bx + tw + pad)
    y1 = min(h, by + tw + pad)

    args.outdir.mkdir(parents=True, exist_ok=True)
    Image.fromarray(mask).save(args.outdir / "mask.png")
    Image.fromarray(heat).save(args.outdir / "heat.png")

    # side-by-side crop: ref | render | abs diff
    crop_ref = ref_im.crop((x0, y0, x1, y1))
    crop_rend = Image.fromarray(rend.astype(np.uint8)).crop((x0, y0, x1, y1))
    crop_diff = Image.fromarray(
        np.clip(diff[y0:y1, x0:x1], 0, 255).astype(np.uint8)
    )
    gap = 8
    cw, ch = crop_ref.size
    strip = Image.new("RGB", (cw * 3 + gap * 2, ch), (20, 20, 20))
    strip.paste(crop_ref, (0, 0))
    strip.paste(crop_rend, (cw + gap, 0))
    strip.paste(crop_diff, (cw * 2 + gap * 2, 0))
    strip.save(args.outdir / "worst-crop.png")

    report = {
        "canvas": {"width": w, "height": h},
        "mae": round(mae, 3),
        "score": round(score, 4),
        "worst_tile": {
            "mae": round(best[0], 3),
            "tile_xy": [bx, by],
            "tile_size": tw,
            "crop_box": [x0, y0, x1, y1],
        },
        "files": {
            "mask": str((args.outdir / "mask.png").resolve()),
            "heat": str((args.outdir / "heat.png").resolve()),
            "worst_crop": str((args.outdir / "worst-crop.png").resolve()),
        },
        "hint": "Patch surgically using worst-crop.png (left=ref, mid=render, right=abs diff). Prefer str_replace; never full rewrite.",
    }
    (args.outdir / "report.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    print(json.dumps(report, indent=2))


if __name__ == "__main__":
    main()
