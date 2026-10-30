# /// script
# requires-python = ">=3.11"
# ///
"""Make a clean image of one subject (a character, an object) from the reference, ready for image-to-3D.

    uv run isolate_subject.py <reference.png> <out.png> --describe "<the subject and its distinctive details>"
                              [--background "plain flat light-grey"] [--front] [--aspect 1:1] [--model openai/gpt-image-2]

- GPT Image 2 via OpenRouter (OPENROUTER_API_KEY from the environment, ./.env or ~/.env; never printed). ~US$ 0.02–0.15.
- --describe must name what makes the subject unique (number of eyes, asymmetries, light strips, logos): models
  simplify what is not named.
- By default it keeps the view of the reference (e.g. three-quarters); --front asks for a front view instead.
- Writes <out.png> and <out>.json (prompt, cost, seconds). Look at the result before spending on 3D.
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
from pathlib import Path

API = 'https://openrouter.ai/api/v1/images'


def key() -> str:
    if os.environ.get('OPENROUTER_API_KEY'):
        return os.environ['OPENROUTER_API_KEY']
    for env in (Path.cwd() / '.env', Path.home() / '.env'):
        if env.exists():
            for line in env.read_text(encoding='utf-8').splitlines():
                if line.strip().startswith('OPENROUTER_API_KEY='):
                    return line.split('=', 1)[1].strip().strip('"').strip("'")
    sys.exit('ERROR: set OPENROUTER_API_KEY (environment, .env or ~/.env).')


def data_url(p: Path) -> str:
    mime = 'image/png' if p.suffix.lower() == '.png' else 'image/jpeg'
    return f'data:{mime};base64,' + base64.b64encode(p.read_bytes()).decode()


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('reference')
    ap.add_argument('out')
    ap.add_argument('--describe', required=True)
    ap.add_argument('--background', default='plain flat light-grey')
    ap.add_argument('--front', action='store_true', help='ask for a front view instead of keeping the reference view')
    ap.add_argument('--aspect', default='1:1')
    ap.add_argument('--model', default='openai/gpt-image-2')
    a = ap.parse_args()
    view = ('Front view, facing the camera.' if a.front else
            'Keep exactly the same viewing angle and pose as in IMAGE 1 (if it is turned three-quarters, keep it turned).')
    prompt = (f'Studio product render of the exact subject from IMAGE 1, isolated: {a.describe}. Keep its design faithfully: '
              f'every distinctive detail, asymmetry, light and marking exactly as in IMAGE 1. {view} The whole subject fully '
              f'visible and centered with generous margin, nothing cropped. {a.background} background. Soft even studio lighting so '
              'all surfaces and details are readable. Remove everything else: no interface, no text, no rings, no particles, no '
              'background glow, no floor reflections.')
    body = {'model': a.model, 'prompt': prompt, 'n': 1, 'aspect_ratio': a.aspect, 'resolution': '1K',
            'input_references': [{'type': 'image_url', 'image_url': {'url': data_url(Path(a.reference))}}]}
    t0 = time.time()
    req = urllib.request.Request(API, data=json.dumps(body).encode(), method='POST',
                                 headers={'Authorization': f'Bearer {key()}', 'Content-Type': 'application/json'})
    try:
        with urllib.request.urlopen(req, timeout=600) as r:
            data = json.loads(r.read())
    except urllib.error.HTTPError as e:
        sys.exit(f'OpenRouter HTTP {e.code}: {e.read().decode(errors="replace")[:600]}')
    item = (data.get('data') or [{}])[0]
    if not item.get('b64_json'):
        sys.exit(f'no image in the answer: {json.dumps(data)[:400]}')
    out = Path(a.out)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_bytes(base64.b64decode(item['b64_json']))
    cost = (data.get('usage') or {}).get('cost')
    out.with_suffix('.json').write_text(json.dumps({'prompt': prompt, 'cost': cost, 'seconds': round(time.time() - t0, 1)}, indent=1))
    print(out, f'${cost}')


if __name__ == '__main__':
    main()
