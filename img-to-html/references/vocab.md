# Closed CSS vocabulary (img-to-html)

Generate `index.html` **only** with patterns below + measured tokens from `measure.json`.
Do not invent exotic CSS. Prefer absolute layout inside a fixed canvas.

## Root

```css
html, body { margin: 0; padding: 0; background: var(--page-bg); }
#app {
  position: relative;
  width: var(--canvas-w);   /* from measure.canvas.width */
  height: var(--canvas-h);  /* from measure.canvas.height */
  overflow: hidden;
  font-family: var(--font);
  color: var(--text);
}
```

Map `--page-bg` ← `measure.page_bg_guess` or nearest palette hex.
Map palette colors into `--c0 … --cN` from `measure.palette[].hex` (do not invent new hex unless sampling a rim).

## Surfaces

| Token use | CSS pattern |
|-----------|-------------|
| Solid fill | `background: var(--cN);` |
| Gradient | `background: linear-gradient(<angle>deg, <hex> <pct>%, …);` angles ∈ {0,45,90,135,180,225,270,315} |
| Glass | `background: rgba(R,G,B,A); backdrop-filter: blur(<8–40>px) saturate(<100–180>%);` |
| Border | `border: <1–2>px solid rgba(...);` or `border: 1px solid var(--cN);` |
| Radius | `border-radius: 0 \| 8 \| 12 \| 16 \| 20 \| 24 \| 9999px;` |
| Shadow | `box-shadow: <x>px <y>px <blur>px rgba(...);` keep ≤2 shadows |
| Glow | single soft `box-shadow` with accent rgba |

## Layout primitives

- **Absolute region:** `position:absolute; left/top/width/height` in px from plan/OCR boxes when known
- **Flex row/col:** `display:flex; gap: 8|12|16|24;`
- **Stack:** flex column inside a region
- Avoid grid unless the mock is clearly a uniform grid

## Components (only these)

1. **Panel / card** — surface + radius + optional glass
2. **Button** — padding 8–16, radius from set, solid or glass
3. **Input / search** — height 40–56, radius, placeholder color muted
4. **Chip / pill** — `border-radius: 9999px`
5. **Nav row** — icon (inline SVG 16–20) + label
6. **Avatar** — circle `img` or div
7. **Icon button** — square hit area
8. **List item** — title + meta caption
9. **Stat block** — big number + label
10. **Img slot** — `<img src="assets/…">` with exact width/height

## Typography

Use only roles from `typography.json`:
`font-size` from OCR `est_font_px` / font_roles_hint when present.
Weights: 400, 500, 600 only unless measure clearly needs 700.
Colors: palette hex or `rgba` from palette channels.

## Forbidden

- Tailwind / React / CSS-in-JS
- `filter: drop-shadow` stacks > 2
- Random hex not in palette (except measured rim samples)
- Rewriting the whole file during diff patches
