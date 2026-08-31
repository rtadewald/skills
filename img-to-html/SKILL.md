---
name: img-to-html
description: >-
  Pixel-oriented image→HTML: measure.py (palette/OCR/canvas) → compile from a
  closed CSS vocab → Playwright render → diff mask/crop loop (2–3×). Assets via
  openrouter-img edits. Use when the user mentions img-to-html or wants a
  pixel-perfect HTML recreation of a mock/screenshot.
disable-model-invocation: true
---

# Img → HTML (measure → compile → diff)

Recreate a reference UI as portable **`index.html`** under `design-systems/<slug>/`.

**Core idea:** stop “looking and freehanding HTML”. **Measure in code**, generate inside a **closed CSS vocabulary**, correct with **pixel diff + worst-region crops**.

**Standalone.** Only external skill: **`openrouter-img`** for raster assets (generated/edited — **not** crops of the reference).

Do not narrate. Execute, then report paths.

## INPUT

`$SOURCE` image path or attachment. If missing, ask.

## OUTPUT

```
design-systems/<slug>/
  reference.[ext]
  measure.json              ← scripts/measure.py
  plan.md                   ← short blocked plan
  image-slots.json
  typography.json
  assets/                   ← openrouter-img (edits from reference)
  index.html
  review/
    render.png              ← scripts/render.py
    diff-1/ … diff-N/       ← scripts/diff.py (mask, heat, worst-crop, report)
```

- Slug kebab-case from product name; if exists → `-2`, `-3`…
- Do not overwrite slug. Do not modify `$SOURCE`.
- Canvas = `measure.canvas` (fixed px). No responsive pass.

---

## FLOW

```
1. folder + copy reference
2. MEASURE (code)     → measure.json
3. plan.md + image-slots.json  (main; short)
4. PARALLEL:
     typography helper  → typography.json
     images helper      → assets/*
5. COMPILE            → index.html  (from measure + vocab + typography + assets)
6. DIFF LOOP (2–3×):
     render.py → render.png
     diff.py   → review/diff-N/
     Read worst-crop.png (+ report.json)
     surgical str_replace patch on index.html
     stop early if score ≥ 0.92 or mae < 12
7. report paths
```

**No UI subagent for colors.** Palette / OCR / canvas come from `measure.py`. Main (or a thin helper) only *maps* measure → CSS variables + closed components.

Harness-agnostic: typography + images may be Task subagents; measure/render/diff are always local scripts.

---

## STEP 1 — MEASURE (required, code)

```bash
uv run ~/.agents/skills/img-to-html/scripts/measure.py \
  design-systems/<slug>/reference.png \
  --out design-systems/<slug>/measure.json
```

Produces:
- `canvas.width/height`
- `palette[]` quantized hex + share
- `page_bg_guess`, corner samples
- OCR words with boxes, `est_font_px`, `font_roles_hint`

**Use these values.** Do not replace palette hexes with vibes.

---

## STEP 2 — PLAN + SLOTS (main, short)

Blocked `plan.md` only (no ASCII catalog):

```markdown
# <slug>
- canvas: from measure
- mood: …
## Regions (names + rough role)
## CSS vs raster slots
## Watchouts
```

`image-slots.json` — rasters that are not CSS (photo bg, 3D mascot, illustration):

```json
{
  "canvas": { "width": 1440, "height": 900 },
  "slots": [
    {
      "id": "hero-art",
      "filename": "hero-art.png",
      "width": 420,
      "height": 320,
      "aspect_ratio": "4:3",
      "transparent": true,
      "edit_prompt": "Extract/recreate the 3D object only; transparent PNG; no text; no UI chrome"
    }
  ]
}
```

- Always `--input-image` reference via openrouter-img (edit, not text-only invent).
- `transparent: true` → PNG alpha for cutouts/overlays; full-bleed bgs may be opaque.
- Exact `aspect_ratio` / width / height. No baked-in text.

---

## STEP 3 — PARALLEL HELPERS

### Typography

```bash
uv run ~/.agents/skills/img-to-html/scripts/match_font.py \
  --glyph /tmp/glyph.png --text "Sample" --top 5 --limit-fonts 120
```

Write `typography.json` (family, cdn, roles). Prefer OCR `font_roles_hint` for sizes. Weights 400/500/600 — don’t default bold.

### Images

For each slot → `openrouter-img` with `--input-image`, `--aspect-ratio`, transparency rules. Save under `assets/`.

---

## STEP 4 — COMPILE (closed vocabulary)

Read **`references/vocab.md`** in this skill. Build silent `index.html`:

1. `:root` from `measure.palette` + `typography.json` + canvas vars
2. Regions as absolute/flex **only** with vocab primitives
3. Strings from OCR (`measure.ocr.words`) — verify against reference if OCR garbles
4. Glass: `rgba` + `backdrop-filter` when mock shows translucency (estimate alpha; never solid fake glass)
5. `<img src="assets/...">` for slots at planned size
6. No Tailwind/React. No process comments.

---

## STEP 5 — DIFF LOOP (2–3 iterations)

Canvas W/H from `measure.json`.

**Render:**

```bash
uv run --with playwright \
  ~/.agents/skills/img-to-html/scripts/render.py \
  design-systems/<slug>/index.html \
  --width W --height H \
  --out design-systems/<slug>/review/render.png
```

First time on a machine: `uv run --with playwright python -m playwright install chromium`

**Diff:**

```bash
uv run ~/.agents/skills/img-to-html/scripts/diff.py \
  --ref design-systems/<slug>/reference.png \
  --render design-systems/<slug>/review/render.png \
  --outdir design-systems/<slug>/review/diff-N
```

**Patch policy:**
1. Open `review/diff-N/report.json` + **Read** `worst-crop.png` (left=ref, mid=render, right=diff)
2. Optionally glance at `mask.png` / `heat.png`
3. Fix with **surgical `str_replace`** on `index.html` (or one CSS rule). **Never** rewrite the whole file.
4. Regenerate an asset only if the worst region is clearly the raster slot
5. Re-render + re-diff
6. Stop after **3** iterations, or when `score ≥ 0.92` or `mae < 12`

Do **not** ask the model to “compare two full-page screenshots” without the worst-crop — the crop is mandatory.

---

## AGENT ROLES (minimal)

| Role | Does |
|------|------|
| Main | measure → plan/slots → compile → diff loop |
| Typography helper (optional parallel) | `typography.json` only |
| Images helper (optional parallel) | `assets/` only |

No deep “UI token essay” agent. Measurement replaces vibes.

---

## OUT OF SCOPE

- Cropping reference pixels into `assets/` (user prefers generated/edited assets)
- Multi-page / responsive / React / Tailwind
- ASCII wireframe catalogs
- Full-file rewrites during QA

---

## PARKED — Moondream (optional later)

fal `fal-ai/moondream3-preview/detect` + `FAL_KEY` → region boxes to bias layout/OCR clustering. Not required for this flow.
