# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fal-client",
#     "python-dotenv",
#     "Pillow",
# ]
# ///
"""Moondream 3 Preview via fal.ai — detect / query / point / caption / segment."""
from __future__ import annotations

import argparse
import json
import os
import sys
import urllib.request
from pathlib import Path
from typing import Any

from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path.home() / ".env")

ENDPOINTS = {
    "detect": "fal-ai/moondream3-preview/detect",
    "query": "fal-ai/moondream3-preview/query",
    "point": "fal-ai/moondream3-preview/point",
    "caption": "fal-ai/moondream3-preview/caption",
    "segment": "fal-ai/moondream3-preview/segment",
}


def require_key(override: str | None) -> str:
    key = override or os.environ.get("FAL_KEY")
    if not key:
        print("ERROR: Set FAL_KEY in env/.env or pass --api-key.", file=sys.stderr)
        sys.exit(1)
    os.environ["FAL_KEY"] = key
    return key


def image_size(path: Path) -> tuple[int, int]:
    from PIL import Image

    with Image.open(path) as im:
        return im.size  # W, H


def resolve_image_url(image: str, fal_client: Any) -> tuple[str, Path | None]:
    """Local path → upload; http(s) URL → use as-is."""
    if image.startswith(("http://", "https://", "data:")):
        return image, None
    path = Path(image).expanduser().resolve()
    if not path.is_file():
        print(f"ERROR: image not found: {path}", file=sys.stderr)
        sys.exit(1)
    return fal_client.upload_file(str(path)), path


def norm_to_px(obj: dict, w: int, h: int) -> dict:
    x0 = int(round(float(obj["x_min"]) * w))
    y0 = int(round(float(obj["y_min"]) * h))
    x1 = int(round(float(obj["x_max"]) * w))
    y1 = int(round(float(obj["y_max"]) * h))
    x0, x1 = max(0, min(x0, x1)), min(w, max(x0, x1))
    y0, y1 = max(0, min(y0, y1)), min(h, max(y0, y1))
    return {
        "box": [x0, y0, x1, y1],
        "norm": {
            "x_min": float(obj["x_min"]),
            "y_min": float(obj["y_min"]),
            "x_max": float(obj["x_max"]),
            "y_max": float(obj["y_max"]),
        },
    }


def point_to_px(pt: dict, w: int, h: int) -> dict:
    x = int(round(float(pt["x"]) * w))
    y = int(round(float(pt["y"]) * h))
    return {"xy": [x, y], "norm": {"x": float(pt["x"]), "y": float(pt["y"])}}


def draw_overlay(path: Path, detections: list[dict], out: Path) -> None:
    from PIL import Image, ImageDraw

    im = Image.open(path).convert("RGBA")
    overlay = Image.new("RGBA", im.size, (0, 0, 0, 0))
    draw = ImageDraw.Draw(overlay)
    colors = [
        (0, 255, 128, 220),
        (0, 180, 255, 220),
        (255, 200, 0, 220),
        (255, 80, 160, 220),
        (180, 120, 255, 220),
    ]
    for i, det in enumerate(detections):
        color = colors[i % len(colors)]
        for item in det.get("objects", []):
            x0, y0, x1, y1 = item["box"]
            draw.rectangle([x0, y0, x1, y1], outline=color, width=2)
            label = det.get("prompt", "")
            if label:
                draw.text((x0 + 4, y0 + 4), label, fill=color)
        for item in det.get("points", []):
            x, y = item["xy"]
            r = 4
            draw.ellipse([x - r, y - r, x + r, y + r], fill=color)
    Image.alpha_composite(im, overlay).convert("RGB").save(out)


def run_subscribe(endpoint: str, arguments: dict) -> dict:
    import fal_client

    return fal_client.subscribe(endpoint, arguments=arguments)


def cmd_detect(args: argparse.Namespace) -> int:
    import fal_client

    require_key(args.api_key)
    url, local = resolve_image_url(args.image, fal_client)
    w = h = None
    if local:
        w, h = image_size(local)
    elif args.width and args.height:
        w, h = args.width, args.height

    prompts = args.prompt or ["card"]
    detections: list[dict] = []
    raw_all: list[dict] = []

    for prompt in prompts:
        raw = run_subscribe(
            ENDPOINTS["detect"],
            {
                "image_url": url,
                "prompt": prompt,
                "preview": bool(args.fal_preview),
            },
        )
        raw_all.append({"prompt": prompt, "raw": raw})
        objects = []
        for obj in raw.get("objects") or []:
            if w and h:
                objects.append(norm_to_px(obj, w, h))
            else:
                objects.append(
                    {
                        "box": None,
                        "norm": {
                            "x_min": float(obj["x_min"]),
                            "y_min": float(obj["y_min"]),
                            "x_max": float(obj["x_max"]),
                            "y_max": float(obj["y_max"]),
                        },
                    }
                )
        detections.append(
            {
                "prompt": prompt,
                "count": len(objects),
                "objects": objects,
                "usage_info": raw.get("usage_info"),
                "preview_url": (raw.get("image") or {}).get("url") if raw.get("image") else None,
            }
        )

    payload = {
        "endpoint": ENDPOINTS["detect"],
        "image": args.image,
        "size": [w, h] if w and h else None,
        "detections": detections,
    }

    text = json.dumps(payload, indent=2)
    if args.out:
        Path(args.out).write_text(text)
        print(args.out)
    else:
        print(text)

    if args.overlay:
        if not local or not w:
            print("ERROR: --overlay needs a local --image", file=sys.stderr)
            return 2
        draw_overlay(local, detections, Path(args.overlay))
        print(args.overlay, file=sys.stderr)

    if args.raw_out:
        Path(args.raw_out).write_text(json.dumps(raw_all, indent=2))

    return 0


def cmd_query(args: argparse.Namespace) -> int:
    import fal_client

    require_key(args.api_key)
    url, _ = resolve_image_url(args.image, fal_client)
    arguments: dict[str, Any] = {
        "image_url": url,
        "prompt": args.prompt,
        "reasoning": not args.no_reasoning,
    }
    if args.temperature is not None:
        arguments["temperature"] = args.temperature
    raw = run_subscribe(ENDPOINTS["query"], arguments)
    payload = {
        "endpoint": ENDPOINTS["query"],
        "image": args.image,
        "prompt": args.prompt,
        "output": raw.get("output"),
        "reasoning": raw.get("reasoning"),
        "usage_info": raw.get("usage_info"),
    }
    text = json.dumps(payload, indent=2)
    if args.out:
        Path(args.out).write_text(text)
        print(args.out)
    else:
        print(text)
    return 0


def cmd_point(args: argparse.Namespace) -> int:
    import fal_client

    require_key(args.api_key)
    url, local = resolve_image_url(args.image, fal_client)
    w = h = None
    if local:
        w, h = image_size(local)
    raw = run_subscribe(
        ENDPOINTS["point"],
        {
            "image_url": url,
            "prompt": args.prompt,
            "preview": bool(args.fal_preview),
        },
    )
    points = []
    for pt in raw.get("points") or []:
        if w and h:
            points.append(point_to_px(pt, w, h))
        else:
            points.append({"xy": None, "norm": {"x": float(pt["x"]), "y": float(pt["y"])}})
    payload = {
        "endpoint": ENDPOINTS["point"],
        "image": args.image,
        "prompt": args.prompt,
        "size": [w, h] if w and h else None,
        "count": len(points),
        "points": points,
        "usage_info": raw.get("usage_info"),
        "preview_url": (raw.get("image") or {}).get("url") if raw.get("image") else None,
    }
    text = json.dumps(payload, indent=2)
    if args.out:
        Path(args.out).write_text(text)
        print(args.out)
    else:
        print(text)
    if args.overlay and local and w:
        draw_overlay(local, [{"prompt": args.prompt, "points": points, "objects": []}], Path(args.overlay))
        print(args.overlay, file=sys.stderr)
    return 0


def cmd_caption(args: argparse.Namespace) -> int:
    import fal_client

    require_key(args.api_key)
    url, _ = resolve_image_url(args.image, fal_client)
    arguments: dict[str, Any] = {"image_url": url, "length": args.length}
    if args.temperature is not None:
        arguments["temperature"] = args.temperature
    raw = run_subscribe(ENDPOINTS["caption"], arguments)
    payload = {
        "endpoint": ENDPOINTS["caption"],
        "image": args.image,
        "length": args.length,
        "output": raw.get("output"),
        "usage_info": raw.get("usage_info"),
    }
    text = json.dumps(payload, indent=2)
    if args.out:
        Path(args.out).write_text(text)
        print(args.out)
    else:
        print(text)
    return 0


def _parse_floats(spec: str) -> list[float]:
    parts = [p.strip() for p in spec.replace(" ", "").split(",") if p.strip()]
    try:
        return [float(p) for p in parts]
    except ValueError:
        print(f"ERROR: bad coords '{spec}' (expected comma-separated floats)", file=sys.stderr)
        sys.exit(2)


def _normalize_coords(vals: list[float], w: int | None, h: int | None) -> list[float]:
    """If any value > 1 and size known, treat as pixels → normalize."""
    if w and h and any(v > 1.0 for v in vals):
        out = []
        for i, v in enumerate(vals):
            out.append(v / w if i % 2 == 0 else v / h)
        return out
    return vals


def parse_spatial_references(
    ref_points: list[str] | None,
    ref_boxes: list[str] | None,
    w: int | None,
    h: int | None,
) -> list[Any]:
    refs: list[Any] = []
    for spec in ref_points or []:
        vals = _normalize_coords(_parse_floats(spec), w, h)
        if len(vals) != 2:
            print(f"ERROR: --ref-point needs x,y got '{spec}'", file=sys.stderr)
            sys.exit(2)
        refs.append({"x": vals[0], "y": vals[1]})
    for spec in ref_boxes or []:
        vals = _normalize_coords(_parse_floats(spec), w, h)
        if len(vals) != 4:
            print(f"ERROR: --ref-box needs x1,y1,x2,y2 got '{spec}'", file=sys.stderr)
            sys.exit(2)
        refs.append(vals)
    return refs


def download_url(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    with urllib.request.urlopen(url) as resp:  # noqa: S310 — fal CDN URL
        dest.write_bytes(resp.read())


def cmd_segment(args: argparse.Namespace) -> int:
    import fal_client

    require_key(args.api_key)
    url, local = resolve_image_url(args.image, fal_client)
    w = h = None
    if local:
        w, h = image_size(local)
    elif args.width and args.height:
        w, h = args.width, args.height

    arguments: dict[str, Any] = {
        "image_url": url,
        "object": args.object,
        "preview": bool(args.preview or args.mask_out),
    }
    refs = parse_spatial_references(args.ref_point, args.ref_box, w, h)
    if refs:
        arguments["spatial_references"] = refs

    raw = run_subscribe(ENDPOINTS["segment"], arguments)

    bbox_px = None
    bbox_norm = raw.get("bbox")
    if bbox_norm and w and h:
        bbox_px = norm_to_px(bbox_norm, w, h)

    mask_url = (raw.get("image") or {}).get("url") if raw.get("image") else None
    mask_path = None
    if args.mask_out and mask_url:
        mask_path = str(Path(args.mask_out).resolve())
        download_url(mask_url, Path(args.mask_out))
        print(args.mask_out, file=sys.stderr)
    elif args.mask_out and not mask_url:
        print("WARN: no mask image in response (object missing?)", file=sys.stderr)

    payload = {
        "endpoint": ENDPOINTS["segment"],
        "image": args.image,
        "object": args.object,
        "size": [w, h] if w and h else None,
        "bbox": bbox_px,
        "bbox_norm": bbox_norm,
        "path": raw.get("path"),
        "mask_url": mask_url,
        "mask_file": mask_path,
        "spatial_references": refs or None,
        "usage_info": raw.get("usage_info"),
    }
    text = json.dumps(payload, indent=2)
    if args.out:
        Path(args.out).write_text(text)
        print(args.out)
    else:
        print(text)
    return 0


def build_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--api-key", help="Override FAL_KEY")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("detect", help="Bounding boxes for each --prompt")
    d.add_argument("--image", required=True, help="Local path or https URL")
    d.add_argument("--prompt", action="append", help="Object class (repeatable). Default: card")
    d.add_argument("--out", help="Write JSON path (else stdout)")
    d.add_argument("--overlay", help="Draw boxes on local image → PNG")
    d.add_argument("--fal-preview", action="store_true", help="Ask fal for annotated preview URL")
    d.add_argument("--raw-out", help="Save raw fal responses JSON")
    d.add_argument("--width", type=int, help="Width if --image is URL (for px boxes)")
    d.add_argument("--height", type=int, help="Height if --image is URL")
    d.set_defaults(func=cmd_detect)

    q = sub.add_parser("query", help="VLM question / structured answer")
    q.add_argument("--image", required=True)
    q.add_argument("--prompt", required=True)
    q.add_argument("--out")
    q.add_argument("--no-reasoning", action="store_true")
    q.add_argument("--temperature", type=float)
    q.set_defaults(func=cmd_query)

    pt = sub.add_parser("point", help="Normalized/pixel points for a prompt")
    pt.add_argument("--image", required=True)
    pt.add_argument("--prompt", required=True)
    pt.add_argument("--out")
    pt.add_argument("--overlay")
    pt.add_argument("--fal-preview", action="store_true")
    pt.set_defaults(func=cmd_point)

    c = sub.add_parser("caption", help="Image caption")
    c.add_argument("--image", required=True)
    c.add_argument("--length", choices=["short", "normal", "long"], default="normal")
    c.add_argument("--out")
    c.add_argument("--temperature", type=float)
    c.set_defaults(func=cmd_caption)

    s = sub.add_parser("segment", help="Pixel mask + SVG path + bbox for an object")
    s.add_argument("--image", required=True)
    s.add_argument("--object", required=True, help="Object to segment (API field `object`)")
    s.add_argument("--out", help="Write JSON path (else stdout)")
    s.add_argument(
        "--mask-out",
        help="Download binary mask PNG locally (implies preview)",
    )
    s.add_argument("--preview", action="store_true", help="Request mask image URL")
    s.add_argument(
        "--ref-point",
        action="append",
        help="Spatial ref point x,y (norm 0–1, or pixels if >1). Repeatable",
    )
    s.add_argument(
        "--ref-box",
        action="append",
        help="Spatial ref box x1,y1,x2,y2 (norm or pixels). Repeatable",
    )
    s.add_argument("--width", type=int, help="Width if --image is URL")
    s.add_argument("--height", type=int, help="Height if --image is URL")
    s.set_defaults(func=cmd_segment)

    return p


def main() -> int:
    args = build_parser().parse_args()
    return args.func(args)


if __name__ == "__main__":
    raise SystemExit(main())
