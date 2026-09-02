# /// script
# requires-python = ">=3.10"
# dependencies = [
#     "fal-client",
#     "python-dotenv",
#     "Pillow",
# ]
# ///
"""Typography crops for img-to-html2 via Florence-2 ocr-with-region (1 API call → match by label)."""
from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path

from dotenv import load_dotenv
from PIL import Image, ImageDraw, ImageOps

load_dotenv()
load_dotenv(Path.home() / ".env")

OCR_ENDPOINT = "fal-ai/florence-2-large/ocr-with-region"

TAG_RE = re.compile(r"\[(?:ico|av|img|chart):[^\]]*\]")
TEXT_ROLES = frozenset({"h1", "h2", "h3", "t1", "t2", "t3", "lnk", "btn", "btn2", "btn3", "in"})


def extract_tags(text: str) -> list[tuple[str, str]]:
    """Bracket-aware tag extraction; strips nested [ico:…] from body."""
    results: list[tuple[str, str]] = []
    i = 0
    while i < len(text):
        if text[i] != "[":
            i += 1
            continue
        m = re.match(r"\[(h1|h2|h3|t1|t2|t3|lnk|btn3|btn2|btn|in):", text[i:])
        if not m:
            i += 1
            continue
        role = m.group(1)
        start = i + m.end()
        depth = 1
        j = start
        while j < len(text) and depth > 0:
            if text[j] == "[":
                depth += 1
            elif text[j] == "]":
                depth -= 1
            j += 1
        body = text[start : j - 1]
        body = TAG_RE.sub("", body)
        body = re.sub(r"\s*[│├└┌─].*", "", body)
        body = re.sub(r"\s+", " ", body).strip()
        if body and role in TEXT_ROLES:
            results.append((role, body))
        i = j
    return results


def parse_wireframe_candidates(wireframe: Path) -> dict[str, list[str]]:
    """All tag bodies per role, in wireframe order."""
    tags = extract_tags(wireframe.read_text(encoding="utf-8"))
    candidates: dict[str, list[str]] = {}
    for role, body in tags:
        candidates.setdefault(role, []).append(body)
    return candidates


def pick_wireframe_query(candidates: list[str], boxes: list[dict]) -> tuple[str | None, dict | None, float]:
    """Pick wireframe phrase to locate OCR box — try longest first, prefer exact match."""
    best_query: str | None = None
    best_hit: dict | None = None
    best_score = 0.0
    for query in sorted(candidates, key=len, reverse=True):
        hit, score = find_best_box(boxes, query)
        if not hit:
            continue
        if score == 1.0:
            return query, hit, score
        if score > best_score:
            best_query, best_hit, best_score = query, hit, score
    if best_hit and best_score >= 0.5:
        return best_query, best_hit, best_score
    return None, None, best_score


def norm_label(s: str) -> str:
    return re.sub(r"\s+", " ", s.replace("</s>", "").strip())


def norm_match(s: str) -> str:
    return re.sub(r"\s+", "", norm_label(s)).upper()


def box_from_ocr(entry: dict) -> list[int]:
    x, y, w, h = (
        int(round(entry["x"])),
        int(round(entry["y"])),
        int(round(entry["w"])),
        int(round(entry["h"])),
    )
    return [x, y, x + w, y + h]


def pad_box(box: list[int], pad: int, max_w: int, max_h: int) -> list[int]:
    x0, y0, x1, y1 = box
    return [
        max(0, x0 - pad),
        max(0, y0 - pad),
        min(max_w, x1 + pad),
        min(max_h, y1 + pad),
    ]


def match_score(label: str, query: str) -> float:
    nl, nq = norm_match(label), norm_match(query)
    if nl == nq:
        return 1.0
    if nq in nl or nl in nq:
        return 0.9
    lt, qt = set(nl.split()), set(nq.split())
    if not qt:
        return 0.0
    return len(lt & qt) / len(qt)


def find_best_box(ocr_boxes: list[dict], query: str) -> tuple[dict | None, float]:
    best, best_score = None, 0.0
    for entry in ocr_boxes:
        label = entry.get("label", "")
        score = match_score(label, query)
        if score > best_score:
            best_score = score
            best = {**entry, "matched_label": norm_label(label), "match_score": score}
    if best_score < 0.5:
        return None, best_score
    return best, best_score


def make_hi(crop: Image.Image, min_h: int = 120, border: int = 32) -> Image.Image:
    g = crop.convert("L")
    mean = sum(g.getdata()) / (g.width * g.height)
    rgb = ImageOps.invert(crop.convert("RGB")) if mean < 128 else crop.convert("RGB")
    scale = max(1.0, (min_h + border * 2) / rgb.height)
    if scale > 1.0:
        rgb = rgb.resize((int(rgb.width * scale), int(rgb.height * scale)), Image.LANCZOS)
    hi = Image.new("RGB", (rgb.width + border * 2, rgb.height + border * 2), (255, 255, 255))
    hi.paste(rgb, (border, border))
    return hi


def run_ocr(image: Path) -> dict:
    import fal_client

    url = fal_client.upload_file(str(image))
    return fal_client.subscribe(OCR_ENDPOINT, arguments={"image_url": url})


def ocr_boxes(raw: dict) -> list[dict]:
    results = raw.get("results") or {}
    return list(results.get("quad_boxes") or results.get("bboxes") or [])


def main() -> int:
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--project", type=Path, required=True, help="design-systems/<slug>-regions/")
    p.add_argument("--wireframe", type=Path, help="Defaults to <project>/wireframe.txt")
    p.add_argument("--image", type=Path, help="Defaults to <project>/reference.jpg")
    p.add_argument("--pad", type=int, default=2, help="Padding px around OCR bbox")
    p.add_argument("--overlay", action="store_true", help="Write typography/crops-overlay.png")
    p.add_argument("--role", action="append", help="Only these roles (repeatable)")
    args = p.parse_args()

    project = args.project.resolve()
    wireframe = (args.wireframe or project / "wireframe.txt").resolve()
    image = args.image or project / "reference.jpg"
    if not image.exists():
        for ext in (".jpg", ".jpeg", ".png", ".webp"):
            alt = project / f"reference{ext}"
            if alt.exists():
                image = alt
                break

    typ_dir = project / "typography"
    crops_dir = typ_dir / "crops"
    crops_dir.mkdir(parents=True, exist_ok=True)

    candidates = parse_wireframe_candidates(wireframe)
    if args.role:
        candidates = {k: v for k, v in candidates.items() if k in args.role}

    print(f"OCR {OCR_ENDPOINT} …")
    raw = run_ocr(image)
    boxes = ocr_boxes(raw)
    (typ_dir / "ocr-with-region.json").write_text(json.dumps(raw, indent=2), encoding="utf-8")

    ref = Image.open(image).convert("RGB")
    w, h = ref.size
    overlay = ref.copy() if args.overlay else None
    draw = ImageDraw.Draw(overlay) if overlay else None
    colors = ["#A3E635", "#38BDF8", "#F472B6", "#FB923C", "#C084FC", "#F87171", "#2DD4BF", "#FACC15", "#E879F9"]

    meta: dict[str, dict] = {}
    matches_log: dict[str, dict] = {}
    errors: list[str] = []

    for i, (role, phrases) in enumerate(candidates.items()):
        query, hit, score = pick_wireframe_query(phrases, boxes)
        if not hit or query is None:
            msg = f"{role}: no OCR match for {phrases!r} (best score {score:.2f})"
            errors.append(msg)
            print(f"ERR {msg}", file=sys.stderr)
            continue

        ocr_label = hit["matched_label"]
        box = pad_box(box_from_ocr(hit), args.pad, w, h)
        crop = ref.crop(tuple(box))
        crop_path = crops_dir / f"{role}.png"
        hi_path = crops_dir / f"{role}-hi.png"
        crop.save(crop_path)
        make_hi(crop).save(hi_path)

        meta[role] = {
            "text": ocr_label,
            "wireframe_sample": query,
            "box_px": box,
            "ocr_label": ocr_label,
            "match_score": hit["match_score"],
            "crop": f"typography/crops/{role}.png",
            "crop_hi": f"typography/crops/{role}-hi.png",
        }
        matches_log[role] = meta[role]
        print(
            f"OK  {role}: wireframe={query!r} → ocr_label={ocr_label!r} "
            f"score={hit['match_score']:.2f} box={box} ({box[3]-box[1]}px)"
        )

        if draw:
            color = colors[i % len(colors)]
            x0, y0, x1, y1 = box
            for t in range(2):
                draw.rectangle([x0 - t, y0 - t, x1 + t, y1 + t], outline=color)
            draw.text((x0 + 2, max(0, y0 - 14)), role, fill=color)

    (typ_dir / "ocr-matches.json").write_text(json.dumps(matches_log, indent=2), encoding="utf-8")

    slim = {
        k: {"text": v["text"], "box_px": v["box_px"], "crop": v["crop"], "crop_hi": v["crop_hi"]}
        for k, v in meta.items()
    }
    out = typ_dir / "font-meta.json"
    out.write_text(json.dumps(slim, indent=2), encoding="utf-8")
    # compat: alias antigo
    (typ_dir / "find-font-meta.json").write_text(json.dumps(slim, indent=2), encoding="utf-8")

    if overlay:
        overlay.save(typ_dir / "crops-overlay.png")
        print(typ_dir / "crops-overlay.png")

    print(out)
    print(typ_dir / "ocr-with-region.json")

    if errors:
        print(f"\n{len(errors)} role(s) failed.", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
