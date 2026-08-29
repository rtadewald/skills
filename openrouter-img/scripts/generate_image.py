# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "python-dotenv",
#     "requests",
# ]
# ///
"""Generate images via OpenRouter Image API (/api/v1/images)."""
from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import sys
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()
load_dotenv(Path.home() / ".env")

API = "https://openrouter.ai/api/v1"
TOP10 = [
    "google/gemini-3-pro-image",
    "openai/gpt-image-2",
    "black-forest-labs/flux.2-max",
    "black-forest-labs/flux.2-pro",
    "bytedance-seed/seedream-5-0-pro",
    "bytedance-seed/seedream-5-0-lite",
    "google/gemini-3.1-flash-image",
    "qwen/qwen-image-3-pro",
    "x-ai/grok-imagine-image-2.0",
    "bytedance-seed/seedream-4.5",
]
ALIASES = {
    "pro": "google/gemini-3-pro-image",
    "nb-pro": "google/gemini-3-pro-image",
    "flash": "google/gemini-3.1-flash-image",
    "nb-flash": "google/gemini-3.1-flash-image",
    "gpt2": "openai/gpt-image-2",
    "gpt": "openai/gpt-image-2",
    "flux-max": "black-forest-labs/flux.2-max",
    "flux": "black-forest-labs/flux.2-pro",
    "seedream-pro": "bytedance-seed/seedream-5-0-pro",
    "seedream": "bytedance-seed/seedream-5-0-lite",
    "seedream-4.5": "bytedance-seed/seedream-4.5",
    "qwen": "qwen/qwen-image-3-pro",
    "grok": "x-ai/grok-imagine-image-2.0",
}


def api_key(override: str | None) -> str:
    key = override or os.environ.get("OPENROUTER_API_KEY")
    if not key:
        print("ERROR: Set OPENROUTER_API_KEY in env/.env or pass --api-key.", file=sys.stderr)
        sys.exit(1)
    return key


def headers(key: str) -> dict:
    return {
        "Authorization": f"Bearer {key}",
        "Content-Type": "application/json",
        "HTTP-Referer": "https://github.com/rtadewald/openrouter-img-skill",
        "X-Title": "openrouter-img skill",
    }


def resolve_model(name: str) -> str:
    return ALIASES.get(name.lower(), name)


def data_url(path: str) -> str:
    with open(path, "rb") as f:
        data = f.read()
    mime, _ = mimetypes.guess_type(path)
    mime = mime or "image/png"
    return f"data:{mime};base64,{base64.b64encode(data).decode()}"


def fmt_pricing(pricing: list) -> str:
    if not pricing:
        return "(see usage.cost)"
    parts = []
    for p in pricing:
        bill = p.get("billable", "?")
        unit = p.get("unit", "?")
        cost = p.get("cost_usd")
        var = p.get("variant")
        label = f"{bill}/{unit}"
        if var:
            label += f"[{var}]"
        if cost is None:
            parts.append(label)
        elif unit == "image":
            parts.append(f"{label}=${cost:g}")
        elif unit == "megapixel":
            parts.append(f"{label}=${cost:g}/MP")
        elif unit == "token":
            parts.append(f"{label}=${cost}/tok")
        else:
            parts.append(f"{label}=${cost}")
    return "; ".join(parts)


def cmd_list(key: str, top_only: bool) -> None:
    r = requests.get(f"{API}/images/models", headers=headers(key), timeout=60)
    r.raise_for_status()
    models = r.json().get("data") or []
    want = set(TOP10) if top_only else None
    print(f"{'MODEL':<42} {'RESOLUTIONS':<22} PRICING (endpoint 0)")
    print("-" * 110)
    by_id = {m["id"]: m for m in models}
    order = TOP10 if top_only else sorted(by_id)
    for mid in order:
        m = by_id.get(mid)
        if not m:
            if top_only:
                print(f"{mid:<42} MISSING")
            continue
        try:
            ep = requests.get(f"{API}/images/models/{mid}/endpoints", headers=headers(key), timeout=60)
            ep.raise_for_status()
            endpoints = ep.json().get("endpoints") or []
            e0 = endpoints[0] if endpoints else {}
            res = (e0.get("supported_parameters") or {}).get("resolution") or {}
            vals = ",".join(res.get("values") or []) or "-"
            pricing = fmt_pricing(e0.get("pricing") or [])
        except Exception as exc:
            vals, pricing = "?", f"err:{exc}"
        print(f"{mid:<42} {vals:<22} {pricing}")


def cmd_gen(args) -> None:
    key = api_key(args.api_key)
    model = resolve_model(args.model)
    body: dict = {"model": model, "prompt": args.prompt, "n": 1}
    if args.resolution:
        body["resolution"] = args.resolution
    if args.aspect_ratio:
        body["aspect_ratio"] = args.aspect_ratio
    if args.quality:
        body["quality"] = args.quality
    if args.input_image:
        if not os.path.isfile(args.input_image):
            print(f"ERROR: Input image not found: {args.input_image}", file=sys.stderr)
            sys.exit(1)
        body["input_references"] = [
            {"type": "image_url", "image_url": {"url": data_url(args.input_image)}}
        ]

    r = requests.post(f"{API}/images", headers=headers(key), json=body, timeout=300)
    if r.status_code != 200:
        print(f"ERROR: OpenRouter HTTP {r.status_code}: {r.text[:800]}", file=sys.stderr)
        sys.exit(1)
    data = r.json()
    items = data.get("data") or []
    if not items or not items[0].get("b64_json"):
        print(f"ERROR: No image in response: {json.dumps(data)[:500]}", file=sys.stderr)
        sys.exit(1)

    out = Path(args.filename).expanduser().resolve()
    out.parent.mkdir(parents=True, exist_ok=True)
    raw = base64.b64decode(items[0]["b64_json"])
    out.write_bytes(raw)
    usage = data.get("usage") or {}
    cost = usage.get("cost")
    print(f"Image saved to: {out}")
    print(f"Model: {model}")
    if cost is not None:
        print(f"Cost (OpenRouter usage.cost): ${cost}")


def main() -> None:
    p = argparse.ArgumentParser(description="OpenRouter image generation")
    p.add_argument("--list", action="store_true", help="List models + live pricing")
    p.add_argument("--top", action="store_true", help="With --list, only curated top 10")
    p.add_argument("--prompt", default=None)
    p.add_argument("--filename", default=None)
    p.add_argument("--model", default="flash", help="slug or alias (flash, pro, gpt2, flux, ...)")
    p.add_argument("--resolution", default="1K", help="512|1K|2K|4K (if model supports)")
    p.add_argument("--aspect-ratio", default="16:9")
    p.add_argument("--quality", default=None, help="auto|low|medium|high when supported")
    p.add_argument("--input-image", default=None)
    p.add_argument("--api-key", default=None)
    args = p.parse_args()

    if args.list:
        cmd_list(api_key(args.api_key), top_only=args.top)
        return
    if not args.prompt or not args.filename:
        p.error("--prompt and --filename required (unless --list)")
    cmd_gen(args)


if __name__ == "__main__":
    main()
