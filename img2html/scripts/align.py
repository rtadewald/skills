# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Put a generated image back in place over the reference: find the scale and shift that best match, apply them.

    uv run align.py <reference.png> <generated.png> <out.png> [--window x,y,w,h] [--mask x,y,w,h[;x,y,w,h…]] [--feather 8]

- Image models move and resize what they edit (tens to hundreds of pixels, a few percent of scale). This finds the shift
  by phase correlation at each scale (0.74–1.20), refines it, and writes the generated image re-aligned to the reference.
- --window: the region to match on (default: the whole image). Use a region with strong shapes that both images share.
- --mask: keep the reference's own pixels OUTSIDE these boxes and take the generated pixels only inside them (soft edge
  of --feather px). Use it for plates: only the edited area changes, everything else stays pixel-exact.
Prints the scale, the shift and the mean difference in the window.
"""
from __future__ import annotations

import argparse

import numpy as np
from PIL import Image, ImageDraw, ImageFilter


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('reference')
    ap.add_argument('generated')
    ap.add_argument('out')
    ap.add_argument('--window', default='')
    ap.add_argument('--mask', default='')
    ap.add_argument('--feather', type=float, default=8)
    a = ap.parse_args()
    ref = Image.open(a.reference).convert('RGB')
    W, H = ref.size
    gen = Image.open(a.generated).convert('RGB').resize((W, H), Image.LANCZOS)
    g = lambda im: np.asarray(im.convert('L'), dtype=np.float32) / 255
    r = g(ref)
    if a.window:
        x, y, w, h = map(int, a.window.split(','))
        win = (slice(y, y + h), slice(x, x + w))
    else:
        win = (slice(0, H), slice(0, W))

    def place(k: float, dx: int, dy: int) -> Image.Image:
        w, h = round(W * k), round(H * k)
        canvas = Image.new('RGB', (W, H))
        canvas.paste(gen.resize((w, h), Image.LANCZOS), (round((W - w) / 2 + dx), round((H - h) / 2 + dy)))
        return canvas

    def phase(p: np.ndarray, q: np.ndarray) -> tuple[int, int]:
        F = np.fft.fft2(p - p.mean()) * np.conj(np.fft.fft2(q - q.mean()))
        c = np.fft.ifft2(F / (np.abs(F) + 1e-9)).real
        dy, dx = np.unravel_index(c.argmax(), c.shape)
        return (dx if dx < W // 2 else dx - W), (dy if dy < H // 2 else dy - H)

    rm = np.zeros_like(r); rm[win] = r[win]
    err = lambda k, dx, dy: float(np.abs(g(place(k, dx, dy))[win] - r[win]).mean())
    best = None
    for k in np.arange(0.74, 1.21, 0.02):
        dx, dy = phase(rm, g(place(k, 0, 0)))
        e = err(k, dx, dy)
        if best is None or e < best[0]:
            best = (e, float(k), dx, dy)
    _, k0, dx0, dy0 = best
    for k in np.arange(k0 - 0.02, k0 + 0.021, 0.005):
        for dx in range(dx0 - 6, dx0 + 7, 2):
            for dy in range(dy0 - 6, dy0 + 7, 2):
                e = err(k, dx, dy)
                if e < best[0]:
                    best = (e, float(k), dx, dy)
    e, k, dx, dy = best
    out = place(k, dx, dy)
    if a.mask:
        m = Image.new('L', (W, H), 0)
        d = ImageDraw.Draw(m)
        for box in a.mask.split(';'):
            x, y, w, h = map(int, box.split(','))
            d.rectangle((x, y, x + w, y + h), fill=255)
        out = Image.composite(out, ref, m.filter(ImageFilter.GaussianBlur(a.feather)))
    out.save(a.out)
    print(f'scale {k:.3f} · shift ({dx}, {dy}) px · mean difference in the window {e * 255:.1f}/255 → {a.out}')


if __name__ == '__main__':
    main()
