---
name: ds-from-img
description: >-
  Analyze a UI mock image and build a design-system.html (plus assets/css and
  STACK.md) under design-systems/<slug>/. Use when the user mentions
  ds-from-img or asks to extract a design system from a screenshot/mock.
disable-model-invocation: true
---

# Design System ← Img

You are a Design System Builder working from a **screenshot / mock image**.

Deeply analyze the image, extract its visual language into organized CSS, and write a clean `design-system.html` from scratch that is visually as close as possible to the mock.

## INPUT

Path to the image (`$SOURCE`), or the image attached in the conversation. If missing, ask.

## OUTPUT

Always work under **`design-systems/`** in the user's project cwd (create the folder if it does not exist).

Inside it, create **one folder per design**, named after the product/screen you infer from the image:

- Prefer the product name visible in the UI (logo, title) → slug kebab-case (`langclean`, `acme-dashboard`).
- If no clear name: invent a short slug from the climate + function (`warm-agent-disk`, `neon-chat-ops`).
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
        reference.[ext]   ← copy of $SOURCE
```

---

## STEP 0 — FOLDER + NAME

1. Ensure `design-systems/` exists in the cwd.
2. From the image, choose `<slug>` (see OUTPUT rules).
3. Create `design-systems/<slug>/`. All later files go **only** inside this folder.

---

## STEP 1 — ANALYZE THE IMAGE

Read the image carefully. Memorize before writing any file:

- **Surfaces** — cards, panels, chrome (header/sidebar)
- **Background** — page/app backdrop: flat color, gradient, image, noise, pattern, blur; how it sits behind the UI
- **Colors** — every distinct fill, text, accent, border, chart series (estimate hex/rgba)
- **Typography** — families (serif/sans/mono), sizes, weights, letter-spacing, hierarchy
- **Spacing** — padding, gaps, margins, density of the grid
- **Radius / shadow / border** — how soft or hard the UI feels
- **Layout** — columns, regions, alignment, aspect (e.g. 16:9 desktop)
- **Components** — buttons, inputs, chat bubbles, cards, badges, nav, charts, progress bars, heatmaps, 3D/mascot
- **Decorative effects** — gradients, glows, mesh, glass, patterns
- **Content** — every visible string (labels, numbers, nav, chat). Keep product language; visible UI text in the HTML → **PT-BR**

Do not begin writing CSS/HTML until this step is complete (folder from Step 0 may already exist).

---

## STEP 2 — EXTRACT TOKENS → `assets/css/`

Inside `design-systems/<slug>/`, create CSS split by concern (merge if thin):

| File | Contents |
|------|----------|
| `tokens.css` | `:root` CSS variables: colors, type scale, spacing, radii, shadows |
| `layout.css` | shell, grid, regions, header, columns |
| `components.css` | buttons, cards, inputs, chat, badges, nav |
| `charts.css` | bars, area charts, heatmaps, progress (if present) |
| `effects.css` | gradients, glows, glass, decorative motion (if present) |

Name by function. Prefer variables in `tokens.css`; components consume `var(--…)`.

Copy `$SOURCE` to `design-systems/<slug>/assets/images/reference.[ext]` so the DS folder stays self-contained.

---

## STEP 3 — WRITE `design-system.html` FROM SCRATCH

At `design-systems/<slug>/design-system.html`. This is **not** a caption of the image — it is a working HTML recreation of the screen.

**`<head>`:**
```html
<head>
  <!-- fonts -->
  <link .../>

  <!-- css -->
  <!-- [what this file contains] -->
  <link rel="stylesheet" href="assets/css/tokens.css"/>
  <link rel="stylesheet" href="assets/css/layout.css"/>
  ...
</head>
```

**`<body>`:** recreate every major region from the mock (header, side panel, cards, charts, mascot/3D area, CTAs). Section comments only:

```html
<body>
  <!-- header -->
  ...
  <!-- agent-panel -->
  ...
  <!-- dashboard-grid -->
  ...
</body>
```

**Visual fidelity:**
- Same layout structure and hierarchy as the mock
- Colors / type / radius / shadow match the extracted tokens
- Real content: numbers, labels, chat lines — not lorem
- Charts approximated in HTML/CSS/SVG (same shape and weight as the mock)
- 3D/mascot: use `reference` crop or a placeholder with the same footprint if you cannot recreate the mesh; keep position/overlap
- All visible text in **PT-BR** (do not translate class names, paths, or code)

**Stack:**
- Prefer plain CSS + variables. Add Tailwind / Lucide / Chart lib only if they clearly help fidelity — then list them in `STACK.md`
- Keep HTML compact: no useless blank lines, no unused assets

---

## STEP 4 — WRITE `STACK.md`

At `design-systems/<slug>/STACK.md`. One line per technology actually used. No fluff.

```
- **CSS custom properties** — tokens for color, type, spacing
- **Google Fonts · X** — display/body (if linked)
```

Only what is present in the files you wrote.

---

## QUALITY BAR

Before finishing, verify:

- [ ] Output lives under `design-systems/<slug>/` (never loose next to `$SOURCE`)
- [ ] Every major region of the mock appears in `design-system.html`
- [ ] Tokens live in CSS variables; no random one-off hex scattered without reason
- [ ] Assets resolve relative to `design-system.html`
- [ ] Visible text is PT-BR
- [ ] Opening `design-system.html` in a browser looks like the mock (layout + climate), not a generic dashboard
- [ ] `STACK.md` and `assets/images/reference.*` exist

Show the paths. Stop.
