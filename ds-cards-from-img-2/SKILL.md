---
name: ds-cards-from-img-2
description: >-
  Fast card extraction from a UI mock: one vision Read + one inline PIL pass on
  original bboxes (no disk crops, no sample_cards.py). Silent cards.html under
  design-systems/<slug>-cards/. Use when the user mentions ds-cards-from-img-2
  or wants quicker card replication than ds-cards-from-img.
disable-model-invocation: true
---

# DS Cards ← Img (2 — fast)

Same goal as `ds-cards-from-img` (cards only, measured colors), tuned for **speed**:

- **No** disk crops, **no** `sample_cards.py`, **no** `boxes.json` / `tokens.json` required
- Sample on the **original** via bboxes in **one** inline Python pass
- Still: eyedropper fills/rims, gradient angle, borders, shadows, opacity, layout, quick font match

Prefer this when iterating quickly. Prefer `ds-cards-from-img` when you want the masked script pipeline.

## Communication

- Chat: **paths only**.
- HTML: **silent** (no method notes / galleries).

## INPUT

`$SOURCE` or attached image. Optional scope. Default: all distinct cards visible (cap **8** for speed). Collage → **one** panel.

## OUTPUT

```
design-systems/<slug>-cards/
  cards.html
  reference.[ext]
```

Existing folder → `-2`, `-3`, …. No `crop-*.png`.

---

## SPEED

- **1×** vision Read of the full image.
- **1×** Python/PIL on `reference` (bboxes + samples). No second scripts, no `--auto` detector loops.
- Cap 8 cards. Font match **once**, reuse.

---

## STEP 0 — FOLDER

`design-systems/<slug>-cards/` + `reference.[ext]`.

---

## STEP 1 — READ → BBOXES (IN HEAD / NOTES)

From the one Read: id + `(x0,y0,x1,y1)` per card. Do not write crop files.

---

## STEP 2 — ONE INLINE PIL PASS

On the original, for page bg + each bbox (inset ~10–15% for fill; 1–6px strips for rims):

- Fill hex + ≥3 gradient stops; infer angle (`0/45/90/135/180/…`) → `linear-gradient(<angle>deg, …)`
- Rim TL/TR/BL/BR + edge stops (glow where/which color; note if cards differ)
- Accent hotspots; text light/muted/dark
- Glass vs opaque (bg bleed?) → `backdrop-filter` or solid
- Shadow: offset/blur/color → `box-shadow`

No eyeballing palettes. Keep the script short; print hex to use immediately in CSS (no tokens.json required).

---

## STEP 3 — TYPE (ONCE)

In-memory glyph IoU vs local fonts → best `font-family`. No font prose in HTML.

---

## STEP 4 — `cards.html`

Silent page: sampled bg + all cards (fill → glass → border glow → shadow → content). Strings/layout from the Read.

---

## QUALITY BAR

- [ ] ≤1 Read, ≤1 PIL pass, no disk crops
- [ ] Sampled fills/rims/angles (not invented)
- [ ] Borders/shadows/opacity plausible
- [ ] HTML silent; chat = paths

Show the paths. Stop.
