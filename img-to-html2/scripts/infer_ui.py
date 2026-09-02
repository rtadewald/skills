# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "numpy",
#     "Pillow",
#     "python-dotenv",
# ]
# ///
"""Hybrid UI token inference: deterministic eyedropper + VLM CSS recipe.

Colors / radii / rim / shadow ring come from pixels.
Glass recipe / border structure / blur come from vision (OpenRouter).
Merge rule: measured hex wins over VLM hex when both present.

Usage:
  uv run infer_ui.py \\
    --project design-systems/chatgpt-glass-regions \\
    --type btn
"""
from __future__ import annotations

import argparse
import base64
import json
import math
import os
import re
import sys
import urllib.request
from pathlib import Path

import numpy as np
from dotenv import load_dotenv
from PIL import Image

load_dotenv()
load_dotenv(Path.home() / ".env")

# Reuse sampling helpers from ds-cards-from-img
_CARDS = Path.home() / ".agents/skills/ds-cards-from-img/scripts"
if str(_CARDS) not in sys.path:
    sys.path.insert(0, str(_CARDS))
from sample_cards import (  # noqa: E402
    gradient_angle_and_stops,
    hx,
    mean_patch,
    rim_strips,
)

DEFAULT_MODEL = "google/gemini-3.1-pro-preview"


def estimate_radius_px(sub: np.ndarray) -> int:
    """Walk from TL corner until opaque-ish paint; approx CSS radius."""
    h, w = sub.shape[:2]
    bri = sub.mean(2)
    # threshold: brighter than near-corner bg mean
    bg = float(bri[:3, :3].mean())
    thr = bg + 8
    # along top row from left
    x = 0
    while x < w // 2 and float(bri[max(1, h // 8), x]) < thr:
        x += 1
    # along left col from top
    y = 0
    while y < h // 2 and float(bri[y, max(1, w // 8)]) < thr:
        y += 1
    r = int(round((x + y) / 2))
    # pill heuristic
    if r >= h * 0.4:
        return min(999, max(h // 2, r))
    return max(2, min(r, h // 2))


def outer_shadow_ring(arr: np.ndarray, box: list[int], pad: int = 10) -> dict:
    """Sample pixels just outside the box vs farther bg — soft outer glow/shadow."""
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = box
    # ring just outside
    ox0, oy0 = max(0, x0 - pad), max(0, y0 - pad)
    ox1, oy1 = min(w, x1 + pad), min(h, y1 + pad)
    ring_mask = np.zeros((h, w), dtype=bool)
    ring_mask[oy0:oy1, ox0:ox1] = True
    ring_mask[y0:y1, x0:x1] = False
    # farther annulus
    fx0, fy0 = max(0, x0 - pad * 3), max(0, y0 - pad * 3)
    fx1, fy1 = min(w, x1 + pad * 3), min(h, y1 + pad * 3)
    far_mask = np.zeros((h, w), dtype=bool)
    far_mask[fy0:fy1, fx0:fx1] = True
    far_mask[oy0:oy1, ox0:ox1] = False

    if ring_mask.sum() < 8 or far_mask.sum() < 8:
        return {"detected": False}

    ring = arr[ring_mask]
    far = arr[far_mask]
    ring_m = ring.mean(0)
    far_m = far.mean(0)
    delta = float(np.linalg.norm(ring_m - far_m))
    brighter = float(ring.mean()) > float(far.mean())
    return {
        "detected": delta > 3.0,
        "delta": round(delta, 2),
        "ring_hex": hx(ring_m),
        "far_hex": hx(far_m),
        "kind": "glow" if brighter else "shadow",
        "suggest_blur_px": int(round(min(40, max(6, pad * 1.5 + delta)))),
        "suggest_opacity": round(min(0.55, max(0.08, delta / 80)), 3),
    }


def estimate_fill_alpha(arr: np.ndarray, box: list[int]) -> dict:
    """Compare inset fill vs nearby exterior → rough alpha if glass over bg."""
    h, w = arr.shape[:2]
    x0, y0, x1, y1 = [int(v) for v in box]
    sub = arr[y0:y1, x0:x1]
    sh, sw = sub.shape[:2]
    ix0, iy0 = int(sw * 0.2), int(sh * 0.25)
    ix1, iy1 = int(sw * 0.8), int(sh * 0.75)
    fill = sub[iy0:iy1, ix0:ix1].mean((0, 1))

    # exterior samples: below and left of box
    samples = []
    if y1 + 4 < h:
        samples.append(arr[y1 + 2 : min(h, y1 + 8), x0:x1].mean((0, 1)))
    if x0 > 4:
        samples.append(arr[y0:y1, max(0, x0 - 8) : x0 - 1].mean((0, 1)))
    if not samples:
        return {"alpha": None, "fill_rgb": [int(c) for c in fill], "bg_rgb": None}
    bg = np.mean(samples, axis=0)

    # For each channel: fill ≈ a*fg + (1-a)*bg. Assume fg is near white-ish glass tint
    # Solve alpha assuming fg is the brighter of fill vs a light tint toward white.
    # Simpler: luminance difference ratio.
    fl, bl = float(fill.mean()), float(bg.mean())
    # If fill ~= bg, high transparency or same color
    if abs(fl - bl) < 2:
        alpha = 0.08
    else:
        # assume composite toward a light glass layer L=200 or dark L=40
        target = 200.0 if fl > bl else 40.0
        denom = target - bl
        alpha = (fl - bl) / denom if abs(denom) > 1 else 0.15
        alpha = float(np.clip(alpha, 0.05, 0.55))

    # reconstruct rgba using measured fill as the composite look — report both
    return {
        "alpha_est": round(alpha, 3),
        "fill_rgb": [int(round(c)) for c in fill],
        "bg_rgb": [int(round(c)) for c in bg],
        "fill_hex": hx(fill),
        "bg_hex": hx(bg),
    }


def measure(arr: np.ndarray, box: list[int], typ: str) -> dict:
    x0, y0, x1, y1 = [int(v) for v in box]
    h, w = arr.shape[:2]
    x0, y0 = max(0, x0), max(0, y0)
    x1, y1 = min(w, x1), min(h, y1)
    sub = arr[y0:y1, x0:x1]
    sh, sw = sub.shape[:2]
    if sh < 4 or sw < 4:
        return {"type": typ, "box": [x0, y0, x1, y1], "error": "too-small"}

    ix0, iy0 = max(1, int(sw * 0.12)), max(1, int(sh * 0.15))
    ix1, iy1 = min(sw - 1, int(sw * 0.88)), min(sh - 1, int(sh * 0.85))
    fill_region = sub[iy0:iy1, ix0:ix1]
    fill = hx(fill_region.mean((0, 1)))
    grad = gradient_angle_and_stops(fill_region)
    rims = rim_strips(sub)
    variance = float(fill_region.reshape(-1, 3).var(0).mean())
    glass_likely = variance > 40  # buttons often subtler than big cards

    bri = sub.mean(2)
    text = {}
    light = bri > 160
    muted = (bri > 90) & (bri <= 160)
    if light.sum() > 5:
        text["light"] = hx(sub[light])
    if muted.sum() > 5:
        text["muted"] = hx(sub[muted])

    # top rim brightness vs bottom — lighting cue
    top_bri = float(sub[1:3, sw // 4 : 3 * sw // 4].mean()) if sh > 4 else 0
    bot_bri = float(sub[-3:-1, sw // 4 : 3 * sw // 4].mean()) if sh > 4 else 0

    return {
        "type": typ,
        "box": [x0, y0, x1, y1],
        "size": [sw, sh],
        "fill": fill,
        "gradient": grad,
        "rim": rims,
        "radius_px": estimate_radius_px(sub),
        "glass_likely": glass_likely,
        "fill_variance": round(variance, 2),
        "alpha": estimate_fill_alpha(arr, [x0, y0, x1, y1]),
        "outer": outer_shadow_ring(arr, [x0, y0, x1, y1], pad=max(6, sh // 3)),
        "text": text,
        "lighting": {
            "top_brightness": round(top_bri, 1),
            "bottom_brightness": round(bot_bri, 1),
            "top_lit": top_bri > bot_bri + 3,
        },
    }


def hex_to_rgba(hex_color: str, alpha: float) -> str:
    h = hex_color.lstrip("#")
    if len(h) != 6:
        return f"rgba(255,255,255,{alpha})"
    r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
    return f"rgba({r},{g},{b},{alpha:.3f})"


def call_vlm(crop_path: Path, measured: dict, model: str) -> dict:
    key = os.environ.get("OPENROUTER_API_KEY")
    if not key:
        raise RuntimeError("OPENROUTER_API_KEY missing")

    b64 = base64.b64encode(crop_path.read_bytes()).decode()
    data_url = f"data:image/png;base64,{b64}"
    prompt = (
        "You are a CSS engineer reconstructing ONE UI control from a tight crop "
        "(glassmorphism dashboard). Measured pixel tokens (AUTHORITATIVE for colors) "
        f"are:\n```json\n{json.dumps(measured, indent=2)}\n```\n"
        "Propose a CSS recipe. Prefer real techniques: linear-gradient fills, "
        "gradient borders via border-image or pseudo/mask, inset highlight, "
        "box-shadow glow, backdrop-filter blur, border-radius pill vs rounded.\n"
        "Reply ONLY compact JSON (no markdown):\n"
        "{"
        '"shape":"pill|rounded|rect",'
        '"radius_css":"999px",'
        '"background":{"kind":"linear|solid","css":"..."},'
        '"border":{"kind":"solid|gradient","width_px":1,"css":"..."},'
        '"shadow":[{"css":"..."}],'
        '"glass":{"backdrop_blur_px":12,"notes":"..."},'
        '"typography":{"color":"#...","weight":500,"size_px":null},'
        '"confidence":0-100,'
        '"notes":"short"'
        "}\n"
        "Use the measured hex/rgba values in css strings whenever possible. "
        "Do NOT invent unrelated purple themes."
    )

    payload = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": data_url}},
                ],
            }
        ],
    }
    req = urllib.request.Request(
        "https://openrouter.ai/api/v1/chat/completions",
        data=json.dumps(payload).encode(),
        headers={
            "Authorization": f"Bearer {key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/rtadewald/skills",
            "X-Title": "img-to-html2-infer-ui",
        },
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=120) as resp:
        body = json.loads(resp.read().decode())
    content = body["choices"][0]["message"]["content"]
    return parse_json(content), content


def parse_json(text: str) -> dict:
    text = text.strip()
    m = re.search(r"```(?:json)?\s*([\s\S]*?)```", text)
    if m:
        text = m.group(1).strip()
    try:
        return json.loads(text)
    except Exception:
        i, j = text.find("{"), text.rfind("}")
        if i >= 0 and j > i:
            return json.loads(text[i : j + 1])
        raise


def merge(measured: dict, vision: dict) -> dict:
    """Colors from measured; CSS structure from vision with measured hex injected."""
    alpha = (measured.get("alpha") or {}).get("alpha_est")
    # When fill ≈ bg, alpha solver underestimates — prefer VLM alpha from css or a mid glass default
    if alpha is None or (alpha < 0.12 and measured.get("glass_likely")):
        alpha = None
        vbg = ((vision or {}).get("background") or {}).get("css") or ""
        m = re.search(r"rgba\(\s*\d+\s*,\s*\d+\s*,\s*\d+\s*,\s*([0-9.]+)\s*\)", vbg)
        if m:
            alpha = float(m.group(1))
        else:
            alpha = 0.35
    fill = measured.get("fill") or "#ffffff"
    grad = measured.get("gradient") or {}
    stops = grad.get("stops") or [{"pct": 0, "hex": fill}, {"pct": 100, "hex": fill}]
    angle = grad.get("angle_deg", 180)
    radius = measured.get("radius_px") or 999
    sh = (measured.get("size") or [0, 40])[1]
    if vision and vision.get("shape") == "pill":
        radius_css = "999px"
    elif radius >= sh * 0.4:
        radius_css = "999px"
    else:
        radius_css = vision.get("radius_css") if vision and vision.get("radius_css") else f"{radius}px"

    # Build authoritative background from measured gradient + resolved alpha
    stop_css = ", ".join(
        f"{hex_to_rgba(s['hex'], alpha)} {s.get('pct', 0)}%" for s in stops
    )
    bg_css = f"linear-gradient({angle}deg, {stop_css})"

    rim = measured.get("rim") or {}
    top_c = (rim.get("top") or [fill])[0]
    # Prefer a brighter rim stop for the visible edge (max luma among top strip)
    def luma(hxcol: str) -> float:
        h = hxcol.lstrip("#")
        if len(h) != 6:
            return 0
        r, g, b = int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)
        return 0.2126 * r + 0.7152 * g + 0.0722 * b

    top_stops = rim.get("top") or [fill]
    bright_rim = max(top_stops, key=luma)
    border_css = f"1px solid {hex_to_rgba(bright_rim, min(0.55, alpha + 0.15))}"
    tl = rim.get("TL") or bright_rim
    # Prefer brightest corner for inset highlight
    corners = [rim.get("TL"), rim.get("TR"), rim.get("BL"), rim.get("BR")]
    corners = [c for c in corners if c]
    hi = max(corners, key=luma) if corners else tl
    inset = f"inset 0 1px 0 {hex_to_rgba(hi, 0.45)}"
    # Also add a slightly brighter white-ish top edge if lighting says so / vision asks
    if (vision or {}).get("shape") == "pill" or measured.get("glass_likely"):
        inset = f"inset 0 1px 0 {hex_to_rgba('#c8cce8', 0.22)}, {inset}"

    outer = measured.get("outer") or {}
    shadows = [inset]
    if outer.get("detected"):
        op = outer.get("suggest_opacity", 0.25)
        bl = outer.get("suggest_blur_px", 16)
        col = outer.get("ring_hex") or "#000000"
        if outer.get("kind") == "glow":
            shadows.append(f"0 0 {bl}px {hex_to_rgba(col, op)}")
        else:
            shadows.append(f"0 4px {bl}px {hex_to_rgba(col, op)}")

    v_glass = (vision or {}).get("glass") or {}
    blur = v_glass.get("backdrop_blur_px")
    if blur is None:
        blur = 12 if measured.get("glass_likely") else 0

    v_type = (vision or {}).get("typography") or {}
    text_color = (measured.get("text") or {}).get("light") or (measured.get("text") or {}).get("muted")
    if not text_color:
        text_color = v_type.get("color") or "#e8e8f0"

    font_size = v_type.get("size_px") or max(11, int(round(sh * 0.35)))
    font_weight = v_type.get("weight") or 500

    css = {
        "border_radius": radius_css,
        "background": bg_css,
        "border": border_css,
        "box_shadow": ", ".join(shadows),
        "backdrop_filter": f"blur({int(blur)}px)" if blur else "none",
        "color": text_color,
        "font_size_px": font_size,
        "font_weight": font_weight,
        "height_px": sh,
        "min_width_px": (measured.get("size") or [0, 0])[0],
        "alpha_used": alpha,
    }

    if vision:
        vb = (vision.get("border") or {}).get("css")
        if vb and ("rgba" in vb or "#" in vb):
            css["border_vision"] = vb
        vs = vision.get("shadow") or []
        if vs:
            css["shadow_vision"] = [s.get("css") if isinstance(s, dict) else s for s in vs]
        vbg = (vision.get("background") or {}).get("css")
        if vbg:
            css["background_vision"] = vbg

    return {
        "measured": measured,
        "vision": vision,
        "merged_css": css,
        "merge_policy": "fill/gradient/rim hex from pixels; alpha from VLM when pixel alpha≪glass; blur+shape from VLM",
    }


def write_preview(out_html: Path, merged: dict, label: str = "View all chats") -> None:
    c = merged["merged_css"]
    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8" />
  <title>UI infer — btn</title>
  <style>
    body {{
      margin: 0; min-height: 100vh; display: grid; place-items: center;
      background: #0a0612; font-family: Inter, system-ui, sans-serif;
    }}
    .btn {{
      display: inline-flex; align-items: center; justify-content: center; gap: 8px;
      box-sizing: border-box;
      height: {c['height_px']}px;
      min-width: {c['min_width_px']}px;
      padding: 0 18px;
      border-radius: {c['border_radius']};
      background: {c['background']};
      border: {c['border']};
      box-shadow: {c['box_shadow']};
      backdrop-filter: {c['backdrop_filter']};
      -webkit-backdrop-filter: {c['backdrop_filter']};
      color: {c['color']};
      font-size: {c.get('font_size_px', 13)}px;
      font-weight: {c.get('font_weight', 500)};
      cursor: default;
    }}
  </style>
</head>
<body>
  <button class="btn">{label} <span aria-hidden="true">→</span></button>
</body>
</html>
"""
    out_html.write_text(html)


def load_box(project: Path, typ: str) -> tuple[list[int], Path]:
    man = json.loads((project / "ui-crops" / "manifest.json").read_text())
    for c in man["crops"]:
        if c["type"] == typ:
            return c["box"], project / "ui-crops" / c["file"]
    raise SystemExit(f"type {typ!r} not in ui-crops/manifest.json")


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--project", type=Path, required=True)
    ap.add_argument("--type", default="btn")
    ap.add_argument("--model", default=DEFAULT_MODEL)
    ap.add_argument("--skip-vlm", action="store_true")
    args = ap.parse_args()

    project = args.project.expanduser().resolve()
    ref_path = project / "reference.jpg"
    if not ref_path.exists():
        for ext in (".png", ".jpeg", ".webp"):
            alt = project / f"reference{ext}"
            if alt.exists():
                ref_path = alt
                break

    box, crop_path = load_box(project, args.type)
    arr = np.asarray(Image.open(ref_path).convert("RGB"))
    measured = measure(arr, box, args.type)

    vision = None
    raw_vision = None
    if not args.skip_vlm:
        vision, raw_vision = call_vlm(crop_path, measured, args.model)

    merged = merge(measured, vision or {})
    out_dir = project / "ui-infer" / args.type
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / "measured.json").write_text(json.dumps(measured, indent=2) + "\n")
    if vision is not None:
        (out_dir / "vision.json").write_text(json.dumps(vision, indent=2) + "\n")
        (out_dir / "vision-raw.txt").write_text(raw_vision or "")
    (out_dir / "merged.json").write_text(json.dumps(merged, indent=2) + "\n")
    write_preview(out_dir / "preview.html", merged)

    print(out_dir / "merged.json")
    print(out_dir / "preview.html")
    css = merged["merged_css"]
    print("--- merged CSS ---")
    for k, v in css.items():
        if k.endswith("_vision"):
            continue
        print(f"  {k}: {v}")
    if vision:
        print(f"vision confidence: {vision.get('confidence')} shape={vision.get('shape')}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
