# /// script
# requires-python = ">=3.11"
# ///
"""Run one image through several image-to-3D models on fal.ai, in parallel, and download the GLBs.

    uv run image_to_3d.py <subject.png> <out_dir> [--models tripo,trellis2,rodin | all]

Writes <out_dir>/<model>.glb and <model>.json (endpoint, seconds, size), or <model>.error.txt.
Models (approx. cost per run): tripo (Tripo H3.1, detailed PBR textures, ~US$ 0.40) · trellis2 (~US$ 0.30) ·
rodin (Rodin V2.5, ~US$ 0.40) · hunyuan (Hunyuan 3D v3.1 Pro with PBR, ~US$ 0.53). 1–3 minutes each.
Key: FAL_KEY from the environment, ./.env or ~/.env (never printed).
"""
from __future__ import annotations

import argparse
import base64
import json
import os
import sys
import time
import urllib.error
import urllib.request
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path


def key() -> str:
    if os.environ.get('FAL_KEY'):
        return os.environ['FAL_KEY']
    for env in (Path.cwd() / '.env', Path.home() / '.env'):
        if env.exists():
            for line in env.read_text(encoding='utf-8').splitlines():
                if line.strip().startswith('FAL_KEY='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    sys.exit('ERROR: set FAL_KEY (environment, .env or ~/.env).')


def models(img: str) -> dict[str, tuple[str, dict]]:
    return {
        'tripo': ('tripo3d/h3.1/image-to-3d', {'image_url': img, 'texture': True, 'pbr': True, 'texture_quality': 'detailed'}),
        'trellis2': ('fal-ai/trellis-2', {'image_url': img, 'resolution': 1024}),
        'rodin': ('fal-ai/hyper3d/rodin/v2.5', {'image_urls': [img], 'geometry_file_format': 'glb', 'material': 'PBR'}),
        'hunyuan': ('fal-ai/hunyuan-3d/v3.1/pro/image-to-3d', {'input_image_url': img, 'enable_pbr': True, 'generate_type': 'Normal'}),
    }


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('image')
    ap.add_argument('out')
    ap.add_argument('--models', default='tripo,trellis2,rodin')
    a = ap.parse_args()
    k = key()
    out = Path(a.out)
    out.mkdir(parents=True, exist_ok=True)
    p = Path(a.image)
    img = f"data:image/{'png' if p.suffix.lower() == '.png' else 'jpeg'};base64," + base64.b64encode(p.read_bytes()).decode()
    table = models(img)
    names = list(table) if a.models == 'all' else [m.strip() for m in a.models.split(',')]
    unknown = [m for m in names if m not in table]
    if unknown:
        sys.exit(f'unknown model(s): {unknown}. Available: {list(table)}')

    def req(method: str, url: str, body: dict | None = None) -> dict:
        r = urllib.request.Request(url, method=method, data=json.dumps(body).encode() if body is not None else None,
                                   headers={'Authorization': f'Key {k}', 'Content-Type': 'application/json'})
        try:
            with urllib.request.urlopen(r, timeout=120) as resp:
                return json.loads(resp.read())
        except urllib.error.HTTPError as e:
            raise RuntimeError(f'HTTP {e.code}: {e.read().decode(errors="replace")[:500]}') from None

    def find_glb(o: dict) -> str | None:
        for f in ('model_glb', 'model_mesh'):
            if isinstance(o.get(f), dict) and o[f].get('url'):
                return o[f]['url']
        for v in (o.get('model_urls') or {}).values():
            if isinstance(v, dict) and str(v.get('url', '')).endswith('.glb'):
                return v['url']
        return None

    def run(name: str) -> str:
        endpoint, body = table[name]
        t0 = time.time()
        try:
            q = req('POST', f'https://queue.fal.run/{endpoint}', body)
            while True:
                time.sleep(5)
                if req('GET', q['status_url']).get('status') == 'COMPLETED':
                    break
                if time.time() - t0 > 1200:
                    raise RuntimeError('took more than 20 min')
            res = req('GET', q['response_url'])
            url = find_glb(res)
            if not url:
                raise RuntimeError(f'no GLB in the answer: {json.dumps(res)[:400]}')
            urllib.request.urlretrieve(url, out / f'{name}.glb')
            info = {'endpoint': endpoint, 'seconds': round(time.time() - t0), 'bytes': (out / f'{name}.glb').stat().st_size}
            (out / f'{name}.json').write_text(json.dumps(info, indent=1))
            return f'{name}: ok in {info["seconds"]} s, {info["bytes"] // 1024} KB'
        except Exception as e:  # noqa: BLE001
            (out / f'{name}.error.txt').write_text(str(e))
            return f'{name}: ERROR {e}'

    with ThreadPoolExecutor(len(names)) as ex:
        for line in ex.map(run, names):
            print(line, flush=True)


if __name__ == '__main__':
    main()
