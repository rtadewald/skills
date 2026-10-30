# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Compare a screenshot of the page with the reference image: where and how much they differ.

    uv run compare.py <reference.png> <shot.png> <out_dir> [--regions "name:x,y,w,h;name2:x,y,w,h"]

Writes to <out_dir>: side-by-side.jpg (reference | page) · blend.jpg (50 %) · diff.jpg (heat map) and, per region,
zoom-<name>.jpg (reference | page, enlarged). Prints the mean luminance difference (0–255), full screen and per region.
Coordinates are in reference pixels.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('reference')
    ap.add_argument('shot')
    ap.add_argument('out')
    ap.add_argument('--regions', default='')
    a = ap.parse_args()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    ref = Image.open(a.reference).convert('RGB')
    shot = Image.open(a.shot).convert('RGB').resize(ref.size, Image.LANCZOS)
    lum = lambda im: np.asarray(im).astype(np.float32) @ np.array([0.299, 0.587, 0.114], np.float32)
    diff = np.abs(lum(ref) - lum(shot))

    side = Image.new('RGB', (ref.width * 2, ref.height))
    side.paste(ref, (0, 0))
    side.paste(shot, (ref.width, 0))
    side.save(out / 'side-by-side.jpg', quality=88)
    Image.blend(ref, shot, 0.5).save(out / 'blend.jpg', quality=88)
    heat = np.clip(diff * 4, 0, 255).astype(np.uint8)
    Image.fromarray(np.stack([heat, heat // 2, 255 - heat], -1)).save(out / 'diff.jpg', quality=88)

    print(f'mean luminance difference: {diff.mean():.2f}/255 (full screen)')
    for item in filter(None, a.regions.split(';')):
        name, box = item.split(':')
        x, y, w, h = map(int, box.split(','))
        print(f'  {name:<14} {diff[y:y + h, x:x + w].mean():6.2f}/255')
        z = Image.new('RGB', (w * 2 + 4, h), (90, 90, 90))
        z.paste(ref.crop((x, y, x + w, y + h)), (0, 0))
        z.paste(shot.crop((x, y, x + w, y + h)), (w + 4, 0))
        k = max(1, 1000 // (w * 2))
        z.resize((z.width * k, z.height * k), Image.NEAREST).save(out / f'zoom-{name}.jpg', quality=90)


if __name__ == '__main__':
    main()
