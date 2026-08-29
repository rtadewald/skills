---
name: design-system-from-svg
description: >-
  Analyze a UI wireframe or mock SVG and build a design-system.html (plus
  assets/css and STACK.md) under design-systems/<slug>/. Use when the user
  mentions design-system-from-svg or asks to extract a design system from SVG.
disable-model-invocation: true
---

# Design System ← SVG

You are a Design System Builder working from an **SVG** (wireframe or detailed UI mock).

Read the SVG structure (regions, labels, hierarchy). If it is a gray wireframe, invent a coherent product climate (palette, type, materials) that fits the app intent in the labels. If the SVG already has colors/styles, extract them. Write a clean `design-system.html` that turns the map into a real screen.

## INPUT

Path to the `.svg` (`$SOURCE`). If missing, ask.

## OUTPUT

Always work under **`design-systems/`** in the user's project cwd (create the folder if it does not exist).

Inside it, create **one folder per design**, named after the product/screen you infer from the SVG labels:

- Prefer the product name in the SVG → slug kebab-case (`langclean`, `acme-dashboard`).
- If no clear name: invent a short slug from climate + function.
- If the slug folder already exists, append `-2`, `-3`, … — do not overwrite.

Does not modify `$SOURCE`.
Do not print a long explanation. Execute, then show the paths created.

```
design-systems/
  <slug>/
    design-system.html
    STACK.md
    assets/
      css/
        tokens.css
        layout.css
        components.css
        ...
      images/
        reference.svg   ← copy of $SOURCE
```

---

## STEP 0 — FOLDER + NAME

1. Ensure `design-systems/` exists in the cwd.
2. From the SVG, choose `<slug>`.
3. Create `design-systems/<slug>/`. All later files go **only** inside this folder.

---

## STEP 1 — ANALYZE THE SVG

Read the full SVG. Memorize:

- **Layout** — window, columns, regions, what sits outside the chrome
- **Regions** — each box and its label (chat, treemap, table, agent…)
- **Hierarchy** — what is highlighted / active vs secondary
- **Content hints** — paths, metrics, button names in the labels
- **If colored SVG** — fills, strokes, fonts already present
- **If wireframe (gray)** — no palette yet; you will propose one that fits the product

Do not begin writing CSS/HTML until this step is complete.

---

## STEP 2 — EXTRACT / INVENT TOKENS → `assets/css/`

Inside `design-systems/<slug>/`:

| File | Contents |
|------|----------|
| `tokens.css` | `:root` variables: colors, type, spacing, radii, shadows |
| `layout.css` | shell, grid, regions from the SVG map |
| `components.css` | buttons, cards, inputs, chat, nav… |
| `charts.css` | if the SVG implies charts / heatmaps / progress |
| `effects.css` | glass, glow, motion if the product wants it |

Wireframe source: invent a harmonic palette and climate; do not ship a generic teal SaaS look.
Colored SVG: respect extracted colors first.

Copy `$SOURCE` to `assets/images/reference.svg`.

---

## STEP 3 — WRITE `design-system.html` FROM SCRATCH

At `design-systems/<slug>/design-system.html` — a working HTML screen, not a redraw of the wireframe strokes.

- Same region map as the SVG
- Real UI: typography, surfaces, content (PT-BR for visible text)
- Prefer CSS variables; keep HTML compact
- List real stack in `STACK.md`

---

## STEP 4 — WRITE `STACK.md`

One line per technology actually used. No fluff.

---

## QUALITY BAR

- [ ] Output under `design-systems/<slug>/`
- [ ] Regions from the SVG are present as real UI
- [ ] Tokens in CSS variables
- [ ] Visible text in PT-BR
- [ ] `reference.svg` + `STACK.md` exist

Show the paths. Stop.
