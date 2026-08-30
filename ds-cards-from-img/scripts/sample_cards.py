#!/usr/bin/env python3
"""Fast card sampling for ds-cards-from-img.

Given a reference image + optional boxes JSON, refine each region and sample
fill / gradient angle / rim strips / accents — all in-memory (no vision).

Usage:
  python3 sample_cards.py reference.jpg --boxes boxes.json --out tokens.json
  python3 sample_cards.py reference.jpg --auto --out tokens.json

boxes.json:
  {"cards":[{"id":"metric-1","box":[x0,y0,x1,y1]}, ...]}

Does not call any vision API. Optional --write-crops only when QA is requested.
"""
from __future__ import annotations

import argparse
import json
import math
import sys
from pathlib import Path

try:
    import numpy as np
    from PIL import Image
except ImportError as e:
    print("needs Pillow + numpy:", e, file=sys.stderr)
    sys.exit(2)


def hx(rgb) -> str:
    rgb = np.asarray(rgb, dtype=np.float64).reshape(-1, 3).mean(0)
    return "#{:02x}{:02x}{:02x}".format(*(int(max(0, min(255, x))) for x in rgb))


def mean_patch(arr: np.ndarray, x: int, y: int, r: int = 2) -> np.ndarray:
    h, w = arr.shape[:2]
    return arr[max(0, y - r) : y + r + 1, max(0, x - r) : x + r + 1].mean((0, 1))


def gradient_angle_and_stops(sub: np.ndarray, n_stops: int = 5) -> dict:
    """Compare horizontal vs vertical variance of mean brightness; pick dominant axis."""
    h, w = sub.shape[:2]
    if h < 8 or w < 8:
        return {"angle_deg": 180, "stops": [hx(sub.mean((0, 1)))]}

    # sample along axes through center band
    cy, cx = h // 2, w // 2
    band = max(2, min(h, w) // 12)
    row = sub[cy - band : cy + band, :].mean(0).mean(1)  # brightness along x
    col = sub[:, cx - band : cx + band].mean(1).mean(1)  # brightness along y

    def spread(v: np.ndarray) -> float:
        return float(v.max() - v.min()) if len(v) else 0.0

    sx, sy = spread(row), spread(col)
    # CSS angle: 180deg = top→bottom (darker often at bottom in UI fills)
    if sy >= sx * 0.85:
        angle = 180
        axis = "vertical"
        idxs = np.linspace(int(h * 0.12), int(h * 0.88), n_stops).astype(int)
        stops = []
        for i, yi in enumerate(idxs):
            pct = int(round(100 * i / (n_stops - 1)))
            strip = sub[yi, int(w * 0.2) : int(w * 0.8)].mean(0)
            stops.append({"pct": pct, "hex": hx(strip)})
    else:
        angle = 90  # left→right in CSS is 90deg
        # refine: if left brighter than right → 90, else 270
        left = sub[:, : w // 3].mean()
        right = sub[:, 2 * w // 3 :].mean()
        angle = 90 if left >= right else 270
        axis = "horizontal"
        idxs = np.linspace(int(w * 0.12), int(w * 0.88), n_stops).astype(int)
        stops = []
        for i, xi in enumerate(idxs):
            pct = int(round(100 * i / (n_stops - 1)))
            strip = sub[int(h * 0.2) : int(h * 0.8), xi].mean(0)
            stops.append({"pct": pct, "hex": hx(strip)})

    # also try 45/135 if diagonal variance is clearly higher
    # (cheap: compare corners)
    tl, tr = sub[2:5, 2:5].mean(), sub[2:5, -5:-2].mean()
    bl, br = sub[-5:-2, 2:5].mean(), sub[-5:-2, -5:-2].mean()
    diag_a = abs(float(tl - br))
    diag_b = abs(float(tr - bl))
    axis_max = max(sx, sy)
    if max(diag_a, diag_b) > axis_max * 1.15:
        if diag_a >= diag_b:
            angle = 135 if float(tl) > float(br) else 315
        else:
            angle = 45 if float(tr) > float(bl) else 225
        axis = "diagonal"
        # resample stops along that diagonal
        stops = []
        for i in range(n_stops):
            t = i / (n_stops - 1)
            if angle in (135, 315):
                yi = int(h * (0.12 + 0.76 * t))
                xi = int(w * (0.12 + 0.76 * t)) if angle == 135 else int(w * (0.88 - 0.76 * t))
            else:
                yi = int(h * (0.12 + 0.76 * t))
                xi = int(w * (0.88 - 0.76 * t)) if angle == 45 else int(w * (0.12 + 0.76 * t))
            yi, xi = min(h - 2, max(1, yi)), min(w - 2, max(1, xi))
            stops.append({"pct": int(round(100 * t)), "hex": hx(mean_patch(sub, xi, yi, 2))})

    return {"angle_deg": angle, "axis": axis, "stops": stops}


def rim_strips(sub: np.ndarray) -> dict:
    h, w = sub.shape[:2]

    def stops(strip: np.ndarray, n: int = 5) -> list:
        if strip.ndim == 1 or len(strip) == 0:
            return [hx(strip)] if len(np.atleast_1d(strip)) else []
        idxs = np.linspace(0, max(0, len(strip) - 1), n).astype(int)
        return [hx(strip[i]) for i in idxs]

    top = sub[1:min(5, h), 2 : w - 2].mean(0) if h > 4 else sub[0]
    bot = sub[max(0, h - 5) : h - 1, 2 : w - 2].mean(0) if h > 4 else sub[-1]
    left = sub[2 : h - 2, 1 : min(5, w)].mean(1) if w > 4 else sub[:, 0]
    right = sub[2 : h - 2, max(0, w - 5) : w - 1].mean(1) if w > 4 else sub[:, -1]
    return {
        "top": stops(top),
        "bottom": stops(bot),
        "left": stops(left),
        "right": stops(right),
        "TL": hx(mean_patch(sub, 4, 3)),
        "TR": hx(mean_patch(sub, w - 5, 3)),
        "BL": hx(mean_patch(sub, 4, h - 5)),
        "BR": hx(mean_patch(sub, w - 5, h - 5)),
    }


def sample_card(arr: np.ndarray, box: list[int], card_id: str) -> dict:
    x0, y0, x1, y1 = [int(v) for v in box]
    h, w = arr.shape[:2]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    sub = arr[y0:y1, x0:x1]
    sh, sw = sub.shape[:2]
    if sh < 6 or sw < 6:
        return {"id": card_id, "box": [x0, y0, x1, y1], "error": "too-small"}

    # inset mask ~12% (avoids border bleed) for fill
    ix0, iy0 = int(sw * 0.12), int(sh * 0.12)
    ix1, iy1 = int(sw * 0.88), int(sh * 0.88)
    fill_region = sub[iy0:iy1, ix0:ix1]
    fill = hx(fill_region.mean((0, 1)))
    grad = gradient_angle_and_stops(fill_region)
    rims = rim_strips(sub)

    # accent hotspots (high chroma)
    s = sub.astype(np.int16)
    chroma = np.maximum(np.maximum(s[:, :, 0], s[:, :, 1]), s[:, :, 2]) - np.minimum(
        np.minimum(s[:, :, 0], s[:, :, 1]), s[:, :, 2]
    )
    bright = sub.mean(2)
    hot = (chroma > 40) & (bright > 60) & (bright < 230)
    accent = None
    if hot.sum() > 8:
        score = chroma + (s[:, :, 0] + s[:, :, 2]) // 4
        score = np.where(hot, score, 0)
        iy, ix = np.unravel_index(int(score.argmax()), score.shape)
        accent = {"hot": hx(sub[iy, ix]), "mean": hx(sub[hot])}

    # opacity heuristic: compare inset fill variance vs near-edge exterior if available
    # (glass often has higher local color variance from bg bleed)
    variance = float(fill_region.reshape(-1, 3).var(0).mean())
    glass_likely = variance > 80  # empirical soft threshold

    # text colors
    bri = sub.mean(2)
    white = bri > 210
    muted = (bri > 100) & (bri < 180)
    dark = (bri > 20) & (bri < 70)
    text = {}
    if white.sum() > 10:
        text["light"] = hx(sub[white])
    if muted.sum() > 20:
        text["muted"] = hx(sub[muted])
    if dark.sum() > 20:
        text["dark"] = hx(sub[dark])

    return {
        "id": card_id,
        "box": [x0, y0, x1, y1],
        "fill": fill,
        "gradient": grad,
        "rim": rims,
        "accent": accent,
        "glass_likely": glass_likely,
        "fill_variance": round(variance, 2),
        "text": text,
    }


def sample_page_bg(arr: np.ndarray) -> dict:
    h, w = arr.shape[:2]
    pts = {
        "tl": (12, 12),
        "tr": (w - 12, 12),
        "bl": (12, h - 12),
        "br": (w - 12, h - 12),
        "c": (w // 2, h // 2),
    }
    return {k: hx(mean_patch(arr, x, y, 4)) for k, (x, y) in pts.items()}


def auto_boxes(arr: np.ndarray, max_cards: int = 12) -> list[dict]:
    """Cheap panel finder: bright-ish islands vs dark/flat bg. Not ML — fast fallback."""
    h, w = arr.shape[:2]
    bri = arr.mean(2)
    # adaptive threshold: panels often differ from median bg
    med = float(np.median(bri))
    # candidates: either much brighter or much darker than median (glass light / dark cards)
    mask = (bri > med + 18) | (bri < med - 25)
    # erode noise
    from numpy.lib.stride_tricks import sliding_window_view

    # connected components via crude flood on downsampled grid
    step = max(4, min(h, w) // 80)
    ys, xs = np.where(mask[::step, ::step])
    if len(xs) == 0:
        return []
    # cluster with simple grid cells merged
    cells = {}
    for y, x in zip(ys, xs):
        cells[(x, y)] = True
    visited = set()
    boxes = []

    def neighbors(p):
        x, y = p
        for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            q = (x + dx, y + dy)
            if q in cells:
                yield q

    for seed in list(cells):
        if seed in visited:
            continue
        stack = [seed]
        visited.add(seed)
        comp = []
        while stack:
            p = stack.pop()
            comp.append(p)
            for q in neighbors(p):
                if q not in visited:
                    visited.add(q)
                    stack.append(q)
        if len(comp) < 12:
            continue
        xs_c = [p[0] for p in comp]
        ys_c = [p[1] for p in comp]
        x0, x1 = min(xs_c) * step, (max(xs_c) + 1) * step
        y0, y1 = min(ys_c) * step, (max(ys_c) + 1) * step
        # pad slightly
        pad = step
        box = [max(0, x0 - pad), max(0, y0 - pad), min(w, x1 + pad), min(h, y1 + pad)]
        area = (box[2] - box[0]) * (box[3] - box[1])
        if area < (h * w) * 0.01 or area > (h * w) * 0.55:
            continue
        boxes.append({"id": f"card-{len(boxes)+1}", "box": box, "area": area})

    boxes.sort(key=lambda b: -b["area"])
    # dedupe heavy overlap
    kept = []
    for b in boxes:
        x0, y0, x1, y1 = b["box"]
        ok = True
        for k in kept:
            kx0, ky0, kx1, ky1 = k["box"]
            ix0, iy0 = max(x0, kx0), max(y0, ky0)
            ix1, iy1 = min(x1, kx1), min(y1, ky1)
            if ix1 > ix0 and iy1 > iy0:
                inter = (ix1 - ix0) * (iy1 - iy0)
                if inter / min((x1 - x0) * (y1 - y0), (kx1 - kx0) * (ky1 - ky0)) > 0.45:
                    ok = False
                    break
        if ok:
            kept.append(b)
        if len(kept) >= max_cards:
            break
    return [{"id": b["id"], "box": b["box"]} for b in kept]


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image")
    ap.add_argument("--boxes", help="JSON with {cards:[{id,box:[x0,y0,x1,y1]}]}")
    ap.add_argument("--auto", action="store_true", help="auto-detect panels (fast heuristic)")
    ap.add_argument("--out", default="tokens.json")
    ap.add_argument("--max-cards", type=int, default=12)
    ap.add_argument("--write-crops", metavar="DIR", help="optional QA crops (off by default)")
    args = ap.parse_args()

    path = Path(args.image)
    im = Image.open(path).convert("RGB")
    arr = np.array(im)

    cards_meta: list[dict] = []
    if args.boxes:
        data = json.loads(Path(args.boxes).read_text())
        cards_meta = data.get("cards") or data
    elif args.auto:
        cards_meta = auto_boxes(arr, max_cards=args.max_cards)
    else:
        print("provide --boxes or --auto", file=sys.stderr)
        return 2

    if not cards_meta:
        print("no cards found", file=sys.stderr)
        return 1

    # cap for speed
    cards_meta = cards_meta[: args.max_cards]

    tokens = {
        "source": str(path),
        "size": [im.size[0], im.size[1]],
        "page_bg": sample_page_bg(arr),
        "cards": [],
    }

    crop_dir = Path(args.write_crops) if args.write_crops else None
    if crop_dir:
        crop_dir.mkdir(parents=True, exist_ok=True)

    for i, c in enumerate(cards_meta):
        cid = c.get("id") or f"card-{i+1}"
        box = c["box"]
        sample = sample_card(arr, box, cid)
        tokens["cards"].append(sample)
        if crop_dir and "error" not in sample:
            x0, y0, x1, y1 = sample["box"]
            im.crop((x0, y0, x1, y1)).save(crop_dir / f"{cid}.png")

    out = Path(args.out)
    out.write_text(json.dumps(tokens, indent=2))
    print(out)
    print(f"cards={len(tokens['cards'])}", file=sys.stderr)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
