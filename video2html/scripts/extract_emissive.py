# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "pillow"]
# ///
"""Extract the textures of a GLB and build an emissive mask from its glowing color (the parts that will light up).

    uv run extract_emissive.py <model.glb> <work_dir> [--hue cyan|blue|ice|red|green|orange|white] [--gain 1.6]

Writes <work_dir>/tex0.png, tex1.png… (every embedded texture), emissive.png (base color × mask, to plug into the
material's emission) and emissive-preview.png (the mask). The base-color texture is found through the first
material (pbrMetallicRoughness.baseColorTexture); --texture overrides it.
Check the preview: only the lights (eyes, strips, screens) should be white.
"""
from __future__ import annotations

import argparse
import io
import json
import struct
from pathlib import Path

import numpy as np
from PIL import Image


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('glb')
    ap.add_argument('work')
    ap.add_argument('--hue', default='cyan')
    ap.add_argument('--gain', type=float, default=1.6)
    ap.add_argument('--texture', type=int, default=None, help='index of the base-color image (default: from the material)')
    a = ap.parse_args()
    work = Path(a.work)
    work.mkdir(parents=True, exist_ok=True)

    b = Path(a.glb).read_bytes()
    n = struct.unpack('<I', b[12:16])[0]
    gltf = json.loads(b[20:20 + n])
    off = 20 + n
    blen = struct.unpack('<I', b[off:off + 4])[0]
    binary = b[off + 8:off + 8 + blen]
    for i, img in enumerate(gltf.get('images', [])):
        bv = gltf['bufferViews'][img['bufferView']]
        s = bv.get('byteOffset', 0)
        Image.open(io.BytesIO(binary[s:s + bv['byteLength']])).save(work / f'tex{i}.png')

    if a.texture is None:
        try:
            tex = gltf['materials'][0]['pbrMetallicRoughness']['baseColorTexture']['index']
            a.texture = gltf['textures'][tex]['source']
        except (KeyError, IndexError):
            a.texture = 0
    print(f'base color: tex{a.texture}.png')
    c = np.asarray(Image.open(work / f'tex{a.texture}.png').convert('RGB')).astype(float) / 255
    r, g, bl = c[..., 0], c[..., 1], c[..., 2]
    mx, mn = c.max(-1), c.min(-1)
    sat = (mx - mn) / (mx + 1e-6)
    bright = np.clip((mx - 0.18) * 4, 0, 1)
    vivid = np.clip((sat - 0.35) * 3, 0, 1)
    hue = {
        'cyan': np.clip((bl - r - 0.08) * 4, 0, 1),
        'blue': np.clip((bl - np.maximum(r, g) - 0.05) * 4, 0, 1),
        'red': np.clip((r - np.maximum(g, bl) - 0.08) * 4, 0, 1),
        'green': np.clip((g - np.maximum(r, bl) - 0.08) * 4, 0, 1),
        'orange': np.clip((r - bl - 0.15) * 4, 0, 1) * np.clip((g - bl) * 4, 0, 1),
    }
    if a.hue == 'ice':   # pale blue lights that are almost white (glowing eyes on a dark visor); white plastic stays out
        mask = np.clip((bl - r - 0.03) * 12, 0, 1) * np.clip((mx - 0.55) * 4, 0, 1) * np.clip((sat - 0.06) * 8, 0, 1)
    elif a.hue == 'white':
        mask = np.clip((mx - 0.75) * 5, 0, 1) * np.clip((0.25 - sat) * 5, 0, 1)
    else:
        mask = hue[a.hue] * vivid * bright
    Image.fromarray(((c * mask[..., None] * a.gain).clip(0, 1) * 255).astype(np.uint8)).save(work / 'emissive.png')
    Image.fromarray((mask * 255).astype(np.uint8)).resize((1024, 1024)).save(work / 'emissive-preview.png')
    print(f'{len(gltf.get("images", []))} textures · glowing area: {100 * (mask > 0.3).mean():.2f}% of texels → {work}')


if __name__ == '__main__':
    main()
