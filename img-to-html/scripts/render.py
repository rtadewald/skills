#!/usr/bin/env python3
"""Render index.html at fixed canvas size → PNG screenshot.

Uses Playwright (Chromium). Install once:
  uv run --with playwright python -m playwright install chromium

Usage:
  uv run --with playwright \\
    ~/.agents/skills/img-to-html/scripts/render.py design-systems/slug/index.html \\
    --width 1440 --height 900 --out design-systems/slug/review/render.png
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("html", type=Path)
    ap.add_argument("--width", type=int, required=True)
    ap.add_argument("--height", type=int, required=True)
    ap.add_argument("--out", type=Path, required=True)
    args = ap.parse_args()

    html = args.html.resolve()
    if not html.is_file():
        print(f"ERROR: missing {html}", file=sys.stderr)
        sys.exit(1)

    try:
        from playwright.sync_api import sync_playwright
    except ImportError:
        print(
            "ERROR: playwright not installed. Run:\n"
            "  uv run --with playwright python -m playwright install chromium",
            file=sys.stderr,
        )
        sys.exit(2)

    args.out.parent.mkdir(parents=True, exist_ok=True)
    uri = html.as_uri()

    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(
            viewport={"width": args.width, "height": args.height},
            device_scale_factor=1,
        )
        page.goto(uri, wait_until="networkidle", timeout=60000)
        # allow fonts/CDNs a beat
        page.wait_for_timeout(400)
        page.screenshot(path=str(args.out), full_page=False, type="png")
        browser.close()

    print(str(args.out.resolve()))


if __name__ == "__main__":
    main()
