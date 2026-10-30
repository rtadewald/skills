# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Screenshot or record an HTML page in the installed Google Chrome, headless, to compare with the reference.

    uv run snap.py <url> <out.png> --shot [--wait 2.5] [--at 0] [--freeze]
    uv run snap.py <url> <out.mp4> [--seconds 9] [--wait 2.5]
    common: [--width 1536 --height 864] [--before "<js>"]

- --wait: seconds to let fonts, textures and CDN scripts load. --at: extra seconds before the screenshot.
- --freeze: pauses GSAP and CSS animations before the screenshot.
- --before: JavaScript run right before the shot/recording (e.g. move the cursor:
  "document.querySelector('.stage').dispatchEvent(new PointerEvent('pointermove',{clientX:150,clientY:200,bubbles:true}))").
- Uses the system Chrome (channel="chrome"): nothing to download. Video comes from Chrome's screencast, assembled at
  30 fps with ffmpeg. WebGL pages that load local files need http:// (serve the folder), not file://.
- Page errors are printed at the end: read them.
"""
from __future__ import annotations

import argparse
import base64
import subprocess
import tempfile
import time
from pathlib import Path

from playwright.sync_api import sync_playwright


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('url')
    ap.add_argument('out')
    ap.add_argument('--shot', action='store_true', help='take a screenshot instead of a recording')
    ap.add_argument('--seconds', type=float, default=9)
    ap.add_argument('--width', type=int, default=1536)
    ap.add_argument('--height', type=int, default=864)
    ap.add_argument('--wait', type=float, default=2.5)
    ap.add_argument('--at', type=float, default=0)
    ap.add_argument('--freeze', action='store_true')
    ap.add_argument('--before', default='')
    a = ap.parse_args()
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)

    with sync_playwright() as p:
        browser = p.chromium.launch(channel='chrome', headless=True, args=['--autoplay-policy=no-user-gesture-required',
                                                                           '--hide-scrollbars', '--enable-unsafe-swiftshader', '--use-angle=metal'])
        page = browser.new_page(viewport={'width': a.width, 'height': a.height}, device_scale_factor=1)
        errors: list[str] = []
        page.on('pageerror', lambda e: errors.append(str(e)))
        page.on('console', lambda m: errors.append(m.text) if m.type == 'error' else None)
        page.goto(a.url, wait_until='networkidle')
        page.wait_for_timeout(a.wait * 1000)
        if a.before:
            page.evaluate(f"() => {{ {a.before}; }}")   # discard the return value (GSAP objects do not serialize)
        if a.shot:
            page.wait_for_timeout(a.at * 1000)
            if a.freeze:
                page.evaluate("window.gsap && gsap.globalTimeline.pause(); document.getAnimations().forEach(x => x.pause())")
            page.screenshot(path=str(out))
        else:
            cdp = page.context.new_cdp_session(page)
            frames: list[tuple[float, bytes]] = []
            on = [True]

            def frame(e):
                if not on[0]:
                    return
                frames.append((e['metadata']['timestamp'], base64.b64decode(e['data'])))
                try:
                    cdp.send('Page.screencastFrameAck', {'sessionId': e['sessionId']})
                except Exception:  # noqa: BLE001
                    pass
            cdp.on('Page.screencastFrame', frame)
            cdp.send('Page.startScreencast', {'format': 'jpeg', 'quality': 88, 'maxWidth': a.width, 'maxHeight': a.height})
            end = time.time() + a.seconds
            while time.time() < end:
                page.wait_for_timeout(100)
            on[0] = False
            cdp.send('Page.stopScreencast')
            with tempfile.TemporaryDirectory() as d:
                lines = []
                for i, (ts, img) in enumerate(frames):
                    f = Path(d) / f'f{i:05d}.jpg'
                    f.write_bytes(img)
                    dur = (frames[i + 1][0] - ts) if i + 1 < len(frames) else 0.05
                    lines.append(f"file '{f}'\nduration {max(dur, 0.001):.4f}")
                lines.append(f"file '{Path(d) / f'f{len(frames) - 1:05d}.jpg'}'")
                (Path(d) / 'list.txt').write_text('\n'.join(lines))
                subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-f', 'concat', '-safe', '0', '-i', str(Path(d) / 'list.txt'),
                                '-vf', f'fps=30,scale={a.width}:{a.height}', '-c:v', 'libx264', '-pix_fmt', 'yuv420p', '-crf', '18',
                                '-t', str(a.seconds), str(out)], check=True)
        browser.close()
    if errors:
        print('page errors:\n  ' + '\n  '.join(errors[:10]))
    print(out)


if __name__ == '__main__':
    main()
