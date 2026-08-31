---
name: ds-cards-from-img
description: >-
  Extract UI cards from a mock with measured fidelity via masked sampling
  (colors, gradient angles, borders, shadows, opacity, layout, font match).
  Balanced for speed: one vision Read + one sample script. Writes silent
  cards.html under design-systems/<slug>-cards/. Use when the user mentions
  ds-cards-from-img or asks to replicate cards from an image.
disable-model-invocation: true
---

# DS Cards ← Img

Recreate **cards only** with measured fidelity. Prefer **mask-local samples** over guessing on the full frame — without spending minutes on per-card vision.
## Balance (speed × precision)

| Do | Don't |
|----|--------|
| **1×** vision Read of the full image (layout + strings) | Re-Read each crop with vision |
| **1×** `scripts/sample_cards.py` (masks in memory → tokens) | Exploratory PIL loops / multiple auto-detect retries |
| Sample fill/rim/gradient **inside each card mask** | Mix neighbor/map pixels into fill |
| Page bg from **outside** cards on the full image | Invent glassmorphism palettes |
| Cap **12** cards; collage → **one** panel | Disk crops + galleries by default |

Precision comes from **masked eyedropper**. Speed comes from **no per-card vision** and a single script pass.

## Communication

- Chat after finish: **paths only**.
- HTML: **silent** — no method notes, titles about “extração”, or crop galleries.

## INPUT

`$SOURCE` or attached image. Optional scope (“só metric”). Default: all cards in scope (max 12).

## OUTPUT

```
design-systems/<slug>-cards/
  cards.html
  reference.[ext]
  tokens.json          ← from sample_cards.py
  boxes.json           ← bboxes fed to the script
```

- Existing slug folder → `-2`, `-3`, …
- `crop-*.png` **only** if user asks QA (`--write-crops`).

Skill root for the script: this skill’s folder (`scripts/sample_cards.py`).

---

## STEP 0 — FOLDER

`design-systems/<slug>-cards/` + copy `reference.[ext]`.

---

## STEP 1 — ONE READ → BOXES

From the single Read:

1. List every card to replicate (or user scope), up to 12.
2. Collage/multi-panel: pick **one** panel; take all cards there.
3. Write `boxes.json`:

```json
{"cards":[{"id":"active-jobs","box":[x0,y0,x1,y1]}, ...]}
```

Rough bboxes OK — the script samples inset masks and edge strips.

---

## STEP 2 — ONE SCRIPT (MASKED SAMPLE)

```bash
python3 <skill>/scripts/sample_cards.py reference.[ext] \
  --boxes boxes.json \
  --out tokens.json
```

Fallback if boxes are hard: `--auto` (fast heuristic panels, not ML). Prefer agent boxes from the Read when possible.

Script measures per card (in-memory crop/mask, no vision):

- `fill` + `gradient.angle_deg` + `gradient.stops` (≥3)
- `rim` strips TL/TR/BL/BR + edge stops (glow location/color)
- `accent` hotspots
- `glass_likely` / fill variance (opaque vs translucent hint)
- `text` light/muted/dark
- `page_bg` corners/center on the full image

**Forbidden:** skipping the script and inventing hex by eye.

---

## STEP 3 — TYPE (ONCE)

- One in-memory glyph crop from the original; IoU vs local fonts.
- Best match → CSS `font-family`. No font essay in HTML.
- Reuse that family for all cards unless a card clearly uses display/serif (then one extra match max).

---

## STEP 4 — HTML FROM TOKENS

Build silent `cards.html` from `tokens.json` + layout from the Read:

- Page bg ← `page_bg`
- Each card ← its tokens: `linear-gradient(<angle>deg, …stops)`, rim mask from `rim`, shadow, glass (`backdrop-filter` when `glass_likely` / mock shows bleed)
- Preserve per-card rim/accent differences when tokens differ
- Interior: positions/strings from the Read; chart strokes from `accent`
- Layer when needed: fill → glass → border glow → flare → shadow → content

---

## QUALITY BAR

- [ ] Masked samples in `tokens.json` (not eyeballed)
- [ ] Gradient angle + stops applied
- [ ] Borders/glows follow rim tokens (variants kept)
- [ ] Opacity/glass + shadows plausible vs tokens + Read
- [ ] Layout/strings match; font from tool match
- [ ] ≤1 vision Read; ≤1 sample script; HTML silent; chat = paths

Show the paths. Stop.
