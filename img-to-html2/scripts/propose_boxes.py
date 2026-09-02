# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fal-client",
#     "python-dotenv",
#     "Pillow",
# ]
# ///
"""Parallel Moondream detect from an agent plan → boxes + overlay (+ optional crops).

No layout tiling. Agent chooses categories; script detects, unions per label, draws.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path.home() / ".env")

DETECT = "fal-ai/moondream3-preview/detect"


def require_key(override: str | None) -> None:
    key = override or os.environ.get("FAL_KEY")
    if not key:
        print("ERROR: Set FAL_KEY in env/.env or pass --api-key.", file=sys.stderr)
        sys.exit(1)
    os.environ["FAL_KEY"] = key


def upload(path: Path) -> str:
    import fal_client

    return fal_client.upload_file(str(path))


def detect_parallel(url: str, jobs: list[dict[str, str]]) -> list[dict[str, Any]]:
    import fal_client

    handlers = []
    for job in jobs:
        h = fal_client.submit(
            DETECT,
            arguments={"image_url": url, "prompt": job["prompt"], "preview": False},
        )
        handlers.append((job, h))

    out: list[dict[str, Any]] = []
    for job, h in handlers:
        raw = h.get()
        out.append(
            {
                "label": job["label"],
                "kind": job["kind"],
                "prompt": job["prompt"],
                "objects": list(raw.get("objects") or []),
            }
        )
    return out


def norm_to_box(obj: dict, w: int, h: int) -> list[int]:
    x0 = int(round(float(obj["x_min"]) * w))
    y0 = int(round(float(obj["y_min"]) * h))
    x1 = int(round(float(obj["x_max"]) * w))
    y1 = int(round(float(obj["y_max"]) * h))
    x0, x1 = max(0, min(x0, x1)), min(w, max(x0, x1))
    y0, y1 = max(0, min(y0, y1)), min(h, max(y0, y1))
    return [x0, y0, x1, y1]


def area(box: list[int]) -> int:
    return max(0, box[2] - box[0]) * max(0, box[3] - box[1])


def union_boxes(boxes: list[list[int]]) -> list[int]:
    return [
        min(b[0] for b in boxes),
        min(b[1] for b in boxes),
        max(b[2] for b in boxes),
        max(b[3] for b in boxes),
    ]


def load_plan(path: Path) -> list[dict[str, str]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    jobs: list[dict[str, str]] = []
    for kind in ("macros", "fonts"):
        for entry in data.get(kind) or []:
            label = str(entry.get("label") or entry.get("id") or "").strip()
            prompt = str(entry.get("prompt") or label).strip()
            if not label or not prompt:
                continue
            jobs.append({"label": label, "prompt": prompt, "kind": kind[:-1]})
    if not jobs:
        # also allow flat "categories": [...]
        for entry in data.get("categories") or []:
            label = str(entry.get("label") or entry.get("id") or "").strip()
            prompt = str(entry.get("prompt") or label).strip()
            if label and prompt:
                jobs.append({"label": label, "prompt": prompt, "kind": "macro"})
    if not jobs:
        raise SystemExit(f"ERROR: plan has no macros/categories/fonts: {path}")
    return jobs


def jobs_from_prompts(prompts: list[str], kind: str) -> list[dict[str, str]]:
    return [{"label": p, "prompt": p, "kind": kind} for p in prompts]


def propose(image: Path, jobs: list[dict[str, str]], min_px: int = 8) -> tuple[dict, dict, float]:
    from PIL import Image

    with Image.open(image) as im:
        w, h = im.size
    canvas = w * h

    t0 = time.perf_counter()
    url = upload(image)
    detections = detect_parallel(url, jobs)
    elapsed = time.perf_counter() - t0

    regions: list[dict] = []
    for det in detections:
        boxes = []
        for obj in det["objects"]:
            box = norm_to_box(obj, w, h)
            if box[2] - box[0] < min_px or box[3] - box[1] < min_px:
                continue
            boxes.append(box)
        if not boxes:
            continue

        # fonts: 1 sample (largest). macros/categories: keep each hit (overlap ok)
        if det["kind"] == "font":
            box = max(boxes, key=area)
            pick = [box]
        else:
            pick = boxes

        for box in pick:
            regions.append(
                {
                    "label": det["label"],
                    "kind": det["kind"],
                    "prompt": det["prompt"],
                    "box": box,
                    "norm": {
                        "x_min": box[0] / w,
                        "y_min": box[1] / h,
                        "x_max": box[2] / w,
                        "y_max": box[3] / h,
                    },
                    "area_frac": round(area(box) / canvas, 5),
                }
            )

    regions.sort(key=lambda r: (0 if r["kind"] == "macro" else 1, r["box"][1], r["box"][0]))
    for i, r in enumerate(regions, 1):
        r["id"] = f"r{i}"

    boxes_out = {
        "source": str(image),
        "size": [w, h],
        "plan": jobs,
        "elapsed_s": round(elapsed, 2),
        "counts": {
            "jobs": len(jobs),
            "raw_objects": sum(len(d["objects"]) for d in detections),
            "regions": len(regions),
        },
        "regions": regions,
    }
    raw = {
        "source": str(image),
        "size": [w, h],
        "detections": detections,
    }
    return boxes_out, raw, elapsed


def draw_overlay(image_path: Path, regions: list[dict], out_path: Path) -> None:
    from PIL import Image, ImageDraw, ImageFont

    im = Image.open(image_path).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    macro_palette = [
        (0, 220, 140, 230),
        (0, 170, 255, 230),
        (100, 255, 220, 230),
        (180, 120, 255, 230),
        (80, 200, 255, 230),
        (140, 255, 180, 230),
        (60, 140, 255, 230),
        (200, 160, 255, 230),
    ]
    font_palette = [
        (255, 200, 40, 230),
        (255, 140, 60, 230),
        (255, 90, 160, 230),
        (255, 255, 120, 230),
        (255, 120, 100, 230),
    ]
    label_color: dict[str, tuple] = {}
    try:
        font = ImageFont.truetype("/System/Library/Fonts/Supplemental/Arial.ttf", 13)
    except OSError:
        font = ImageFont.load_default()

    for reg in regions:
        key = reg["label"]
        if key not in label_color:
            pal = font_palette if reg.get("kind") == "font" else macro_palette
            label_color[key] = pal[len(label_color) % len(pal)]
        color = label_color[key]
        x0, y0, x1, y1 = reg["box"]
        draw.rectangle([x0, y0, x1, y1], outline=color, width=2)
        tag = f"{reg['id']}:{reg['label']}"
        tw = draw.textlength(tag, font=font) if hasattr(draw, "textlength") else 8 * len(tag)
        pad = 3
        draw.rectangle([x0, y0, x0 + int(tw) + pad * 2, y0 + 16 + pad], fill=(*color[:3], 200))
        draw.text((x0 + pad, y0 + 2), tag, fill=(10, 10, 20, 255), font=font)

    Image.alpha_composite(im, overlay).convert("RGB").save(out_path)


def save_crops(image_path: Path, regions: list[dict], crops_dir: Path) -> list[Path]:
    from PIL import Image

    crops_dir.mkdir(parents=True, exist_ok=True)
    im = Image.open(image_path).convert("RGBA")
    paths = []
    for reg in regions:
        x0, y0, x1, y1 = reg["box"]
        crop = im.crop((x0, y0, x1, y1))
        out = crops_dir / f"{reg['id']}-{reg['label']}.png"
        crop.save(out)
        paths.append(out)
    return paths


def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("image", help="Reference image path")
    ap.add_argument("--out-dir", help="Output directory (default: alongside image)")
    ap.add_argument("--api-key", help="Override FAL_KEY")
    ap.add_argument("--plan", help="JSON plan with macros/categories (+ optional fonts)")
    ap.add_argument("--prompt", action="append", help="Ad-hoc prompt (no plan)")
    ap.add_argument("--kind", default="macro", choices=("macro", "font"))
    ap.add_argument("--no-crops", action="store_true")
    args = ap.parse_args()

    require_key(args.api_key)
    image = Path(args.image).expanduser().resolve()
    if not image.is_file():
        print(f"ERROR: image not found: {image}", file=sys.stderr)
        return 1

    out_dir = Path(args.out_dir).expanduser().resolve() if args.out_dir else image.parent
    out_dir.mkdir(parents=True, exist_ok=True)

    if args.plan:
        jobs = load_plan(Path(args.plan).expanduser().resolve())
    elif args.prompt:
        jobs = jobs_from_prompts(args.prompt, args.kind)
    else:
        print("ERROR: pass --plan plan.json (or --prompt …).", file=sys.stderr)
        return 1

    boxes, raw, elapsed = propose(image, jobs)

    boxes_path = out_dir / "boxes.json"
    raw_path = out_dir / "boxes-raw.json"
    overlay_path = out_dir / "boxes-overlay.png"
    boxes_path.write_text(json.dumps(boxes, indent=2), encoding="utf-8")
    raw_path.write_text(json.dumps(raw, indent=2), encoding="utf-8")
    draw_overlay(image, boxes["regions"], overlay_path)

    crop_n = 0
    if not args.no_crops:
        crop_n = len(save_crops(image, boxes["regions"], out_dir / "crops"))

    n = boxes["counts"]["regions"]
    print(f"regions={n} jobs={len(jobs)} crops={crop_n} detect={elapsed:.1f}s parallel")
    print(boxes_path)
    print(overlay_path)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
