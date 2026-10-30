# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright", "pillow"]
# ///
"""Compare candidate Google Fonts with a crop of text from the reference image.

    uv run fonts.py <reference.png> <out.png> --box x0,y0,x1,y1 --text "JARVIS" \
        --fonts "Inter,Manrope,Jost,Turret Road" [--size 24] [--spacing 0.4em] [--weights 300,400,500] [--color "#222"]
        [--background "#fff"]

Writes <out.png>: the crop of the reference on top (enlarged), then one row per font and weight with the same text, at the
same height. Pick the closest shapes (letter widths, terminals, a / g / R / S), then fine-tune size and letter-spacing by
measuring the ink box. Uses the system Google Chrome (headless).
"""
from __future__ import annotations

import argparse
import base64
import io
import tempfile
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('reference')
    ap.add_argument('out')
    ap.add_argument('--box', required=True)
    ap.add_argument('--text', required=True)
    ap.add_argument('--fonts', required=True)
    ap.add_argument('--size', type=float, default=24)
    ap.add_argument('--spacing', default='normal')
    ap.add_argument('--weights', default='300,400,500')
    ap.add_argument('--color', default='')
    ap.add_argument('--background', default='')
    a = ap.parse_args()

    x0, y0, x1, y1 = map(int, a.box.split(','))
    ref = Image.open(a.reference).convert('RGB')
    crop = ref.crop((x0, y0, x1, y1))
    # guess colors: background = the crop's border, text = the tenth of pixels farthest from it
    w, h = crop.size
    px = [crop.getpixel((i % w, i // w)) for i in range(w * h)]
    edge = [px[i] for i in range(len(px)) if i % w in (0, w - 1) or i // w in (0, h - 1)]
    back = tuple(sum(c[i] for c in edge) // len(edge) for i in range(3))
    far = sorted(px, key=lambda c: -sum((c[i] - back[i]) ** 2 for i in range(3)))[:max(1, len(px) // 10)]
    ink = tuple(sum(c[i] for c in far) // len(far) for i in range(3))
    bg = a.background or '#%02x%02x%02x' % back
    fg = a.color or '#%02x%02x%02x' % ink

    k = 3
    big = crop.resize((crop.width * k, crop.height * k), Image.LANCZOS)
    buf = io.BytesIO(); big.save(buf, 'PNG')
    fonts = [f.strip() for f in a.fonts.split(',') if f.strip()]
    weights = [w.strip() for w in a.weights.split(',') if w.strip()]
    families = '&'.join('family=' + f.replace(' ', '+') + ':wght@' + ';'.join(weights) for f in fonts)
    rows = ''.join(
        f'<div class="r"><span class="n">{f} {w}</span><span class="t" style="font-family:\'{f}\';font-weight:{w}">{a.text}</span></div>'
        for f in fonts for w in weights)
    html = f'''<!doctype html><html><head><meta charset="utf-8">
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?{families}&display=block">
<style>body{{margin:16px;background:#ececec;font:12px system-ui}}.ref{{display:block;margin-bottom:12px;border:1px solid #bbb}}
.r{{display:flex;align-items:center;gap:16px;background:{bg};margin:4px 0;padding:6px 10px}}
.n{{width:170px;color:{fg};opacity:.6;font:12px system-ui;flex:none}}
.t{{font-size:{a.size * k}px;letter-spacing:{a.spacing};color:{fg};white-space:nowrap;line-height:1}}</style></head>
<body><img class="ref" src="data:image/png;base64,{base64.b64encode(buf.getvalue()).decode()}">{rows}</body></html>'''
    with tempfile.TemporaryDirectory() as d:
        page_file = Path(d) / 'fonts.html'
        page_file.write_text(html, encoding='utf-8')
        with sync_playwright() as p:
            b = p.chromium.launch(channel='chrome', headless=True)
            pg = b.new_page(viewport={'width': max(900, big.width + 260), 'height': 400}, device_scale_factor=1)
            pg.goto(page_file.as_uri(), wait_until='networkidle')
            pg.wait_for_timeout(1500)
            pg.screenshot(path=a.out, full_page=True)
            b.close()
    print(a.out)


if __name__ == '__main__':
    main()
