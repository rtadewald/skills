# /// script
# requires-python = ">=3.11"
# dependencies = ["numpy", "scipy", "pillow"]
# ///
"""Motion map of a UI video: WHERE something moves, HOW MUCH and WHEN.

    uv run motion_map.py <video.mp4> <out_dir> [--ref-width 1536] [--threshold 0.18] [--min-area 40]

Writes to <out_dir>:
  motion.png    heat map (per-pixel deviation over time) on the first frame, with numbered regions
  regions.json  per region: box (in reference pixels), area, intensity, peak time, active windows, period, activity curve
  curves.png    the activity of each region over time
  frames/       the peak frame of each region (r01.jpg…) and a 3×3 sheet of the video

It does not know WHAT moves or HOW: look at the frames, or use describe_motion.py.
"""
from __future__ import annotations

import argparse
import json
import subprocess
from io import BytesIO
from pathlib import Path

import numpy as np
from PIL import Image, ImageDraw, ImageFont
from scipy import ndimage

W, H = 480, 270  # analysis resolution (16:9)


def read_frames(video: Path, fps: float = 15) -> np.ndarray:
    raw = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(video), '-vf', f'fps={fps},scale={W}:{H},format=gray',
                          '-f', 'rawvideo', '-'], capture_output=True, check=True).stdout
    return np.frombuffer(raw, np.uint8).reshape(-1, H, W).astype(np.float32)


def period(curve: np.ndarray, fps: float) -> float | None:
    """Dominant period (s) by autocorrelation; None if the curve does not repeat."""
    c = curve - curve.mean()
    if np.allclose(c, 0):
        return None
    ac = np.correlate(c, c, 'full')[len(c) - 1:]
    ac /= ac[0]
    for i in range(int(fps * 0.4), len(ac) - 1):  # ignore lags < 0.4 s
        if ac[i] > 0.35 and ac[i] >= ac[i - 1] and ac[i] >= ac[i + 1]:
            return round(i / fps, 2)
    return None


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('video')
    ap.add_argument('out')
    ap.add_argument('--ref-width', type=int, default=1536, help='reference image width (boxes come out in this scale)')
    ap.add_argument('--threshold', type=float, default=0.18, help='fraction of the max deviation that counts as motion')
    ap.add_argument('--min-area', type=int, default=40, help='minimum region area (pixels at analysis resolution)')
    ap.add_argument('--merge', type=float, default=0.7, help='minimum correlation to merge neighbouring pieces')
    ap.add_argument('--split', type=float, default=0.8, help='window (s) to split large regions by peak time; 0 disables')
    a = ap.parse_args()
    video, out = Path(a.video), Path(a.out)
    (out / 'frames').mkdir(parents=True, exist_ok=True)
    fps = 15.0
    f = read_frames(video, fps)
    n = len(f)
    sd = f.std(0)
    base = np.median(f, 0)

    # regions: pixels moving above the threshold, joined by dilation (a beam and its node become one region)
    mask = ndimage.binary_dilation(sd > a.threshold * sd.max(), iterations=3)
    lab, _ = ndimage.label(mask)
    # large regions that join touching things are split by the PEAK TIME of each pixel: what lights up at different
    # times becomes different regions
    peak_px = np.abs(f - base).argmax(0) / fps
    masks = []
    for i in range(1, lab.max() + 1):
        m = lab == i
        if m.sum() < a.min_area:
            continue
        if m.sum() > 0.12 * mask.sum() and a.split:
            bands = np.floor(peak_px / a.split)
            parts = []
            for b in np.unique(bands[m]):
                mm = ndimage.binary_dilation(m & (bands == b) & (sd > a.threshold * sd.max()), iterations=2) & m
                r2, _ = ndimage.label(mm)
                parts += [r2 == j for j in range(1, r2.max() + 1) if (r2 == j).sum() >= a.min_area]
            masks += parts or [m]
        else:
            masks.append(m)
    # merge back neighbouring pieces that move together (correlated activity): a ring that glows as a whole becomes
    # one again; beams that fire at different times stay separate
    curve = lambda m: np.abs(f[:, m] - base[m]).mean(1)
    groups = [[m, curve(m)] for m in masks]
    changed = True
    while changed and len(groups) > 1:
        changed = False
        for i in range(len(groups)):
            near = ndimage.binary_dilation(groups[i][0], iterations=4)
            for j in range(i + 1, len(groups)):
                if not (near & groups[j][0]).any():
                    continue
                ci, cj = groups[i][1], groups[j][1]
                if np.std(ci) and np.std(cj) and np.corrcoef(ci, cj)[0, 1] > a.merge:
                    m = groups[i][0] | groups[j][0]
                    groups[i] = [m, curve(m)]
                    del groups[j]
                    changed = True
                    break
            if changed:
                break
    scale = a.ref_width / W
    regions = []
    for m, _ in groups:
        ys, xs = np.nonzero(m)
        y0, y1, x0, x1 = ys.min(), ys.max() + 1, xs.min(), xs.max() + 1
        act = np.abs(f[:, m] - base[m]).mean(1)  # how far the region is from "rest" in each frame
        active = act > act.min() + 0.5 * (act.max() - act.min())
        windows, start = [], None
        for j, v in enumerate(active):
            if v and start is None:
                start = j
            if (not v or j == n - 1) and start is not None:
                windows.append([round(start / fps, 2), round(j / fps, 2)])
                start = None
        regions.append({
            'box': [round(x0 * scale), round(y0 * scale), round((x1 - x0) * scale), round((y1 - y0) * scale)],
            'area': int(m.sum()), 'intensity': round(float(sd[m].mean()), 2), 'peak_s': round(int(act.argmax()) / fps, 2),
            'active_windows_s': windows, 'period_s': period(act, fps),
            'curve': [round(float(x), 2) for x in act[:: max(1, int(fps / 5))]],  # 5 samples/s
        })
    regions.sort(key=lambda r: -r['intensity'] * r['area'])
    for i, r in enumerate(regions, 1):
        r['id'] = f'r{i:02d}'

    # heat map + boxes
    f0 = subprocess.run(['ffmpeg', '-loglevel', 'error', '-i', str(video), '-vframes', '1', '-vf', f'scale={W * 2}:{H * 2}',
                         '-f', 'image2pipe', '-vcodec', 'png', '-'], capture_output=True, check=True).stdout
    back = Image.open(BytesIO(f0)).convert('RGB')
    heat = (np.clip(sd / sd.max(), 0, 1) * 255).astype(np.uint8)
    color = Image.fromarray(np.stack([heat, (heat * 0.55).astype(np.uint8), np.zeros_like(heat)], -1)).resize(back.size)
    img = Image.blend(Image.eval(back, lambda v: v // 3), color, 0.65)
    d = ImageDraw.Draw(img)
    try:
        font = ImageFont.truetype('/System/Library/Fonts/Helvetica.ttc', 15)
    except OSError:
        font = ImageFont.load_default()
    k2 = 2 * W / a.ref_width
    for r in regions:
        x, y, w, h = [v * k2 for v in r['box']]
        d.rectangle([x, y, x + w, y + h], outline=(80, 200, 255), width=2)
        d.text((x + 3, y + 2), r['id'], fill=(255, 255, 255), font=font)
    img.save(out / 'motion.png')

    # curves
    ch, cw = 46, 720
    cur = Image.new('RGB', (cw + 60, ch * max(1, len(regions)) + 20), (12, 14, 18))
    d = ImageDraw.Draw(cur)
    for i, r in enumerate(regions):
        c = np.array(r['curve'])
        c = (c - c.min()) / (np.ptp(c) or 1)
        y0 = 10 + i * ch
        d.line([(55 + j * cw / max(1, len(c) - 1), y0 + ch - 8 - v * (ch - 14)) for j, v in enumerate(c)], fill=(90, 190, 255), width=2)
        d.text((6, y0 + ch / 2 - 8), r['id'], fill=(220, 220, 220), font=font)
    cur.save(out / 'curves.png')

    # frames: each region's peak + a 3×3 sheet
    for r in regions:
        subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-ss', str(r['peak_s']), '-i', str(video), '-vframes', '1',
                        '-vf', 'scale=960:-2', '-strict', '-1', str(out / 'frames' / f'{r["id"]}.jpg')])
    dur = n / fps
    subprocess.run(['ffmpeg', '-loglevel', 'error', '-y', '-i', str(video), '-vf', f'fps={9 / dur:.4f},scale=640:-2,tile=3x3',
                    '-frames:v', '1', '-strict', '-1', str(out / 'frames' / 'sheet.jpg')])

    (out / 'regions.json').write_text(json.dumps({'video': str(video), 'duration_s': round(dur, 2), 'analysis_fps': fps,
                                                  'ref_width': a.ref_width, 'regions': regions}, indent=1))
    print(f'{len(regions)} regions · {dur:.1f} s → {out}')
    for r in regions:
        print(f"  {r['id']} box={r['box']} int={r['intensity']} peak={r['peak_s']}s period={r['period_s']} active={r['active_windows_s'][:3]}")


if __name__ == '__main__':
    main()
