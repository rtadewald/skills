---
name: design-system-from-html
description: >-
  Analyze an HTML file and extract a clean design system from it. Splits inline
  style/script into assets, classifies SVGs, writes design-system.html + STACK.md.
  Use when the user mentions design-system-from-html or asks to extract a DS from HTML.
---

## INPUT
$SOURCE

## OUTPUT
Creates new files relative to INPUT's folder.
Does not modify INPUT or any existing file.
Do not print anything. Do not explain. Just execute.

---

You are a Design System Builder.

Your job is to deeply analyze the input HTML, extract every inline
asset found into organized files, and write a clean design-system.html
from scratch that is visually identical to the original.

Execute the following steps in order.
Complete each step fully before moving to the next.

---

## STEP 1 — ANALYZE

Read the entire INPUT carefully. Memorize:
- Every color, gradient, shadow, and surface
- Every font, size, weight, spacing, and typographic pattern
- Every animation, keyframe, transition, and hover behavior
- Every UI component: buttons, cards, badges, inputs, accordions
- Every layout pattern: grids, columns, spacing, alignment
- Every decorative effect: backgrounds, glows, beams, patterns
- Every asset referenced: CSS, JS, fonts, images, CDNs
- Every inline `<style>` block and `<script>` block
- Every SVG element and its usage context

Do not begin writing any file until this step is complete.

---

## STEP 2 — EXTRACT INLINE CSS

Scan INPUT for every inline `<style>` block.

For each block:
- Determine what the CSS does
- Save its content to `assets/css/[descriptive-name].css`
- Name by function: e.g. `animations.css`, `components.css`, `buttons.css`
- If multiple blocks serve the same concern, merge into one file

---

## STEP 3 — EXTRACT INLINE JS

Scan INPUT for every inline `<script>` block containing actual JS code.

For each block:
- Determine what the JS does
- Save its content to `assets/js/[descriptive-name].js`
- Name by function: e.g. `scroll-reveal.js`, `accordion.js`, `interactions.js`
- If multiple blocks serve the same concern, merge into one file

Do NOT extract:
- `<script type="application/ld+json">` blocks
- Single-line event handler scripts

---

## STEP 4 — CLASSIFY EVERY SVG

Scan INPUT for every inline `<svg>` element.
Classify each into exactly one of three categories:

**Category A — Lucide icon**
The SVG has `class="lucide lucide-[name]..."` or `data-lucide="[name]"`.
Replace with: `<i data-lucide="[name]" class="[original non-lucide classes]"></i>`
The Lucide JS runtime already linked will render them correctly.
Color classes (text-orange-500, fill-current, etc.) will work as expected.
Do NOT save these as files.

**Category B — Custom SVG using currentColor**
The SVG uses `fill="currentColor"`, `stroke="currentColor"`,
or relies on Tailwind color classes inherited via CSS.
These MUST remain inline — extracting to `<img>` breaks color inheritance.
Do NOT save these as files.
Minify to a single line.

**Category C — Custom SVG with hardcoded colors only**
The SVG uses only hardcoded hex/rgba values and does not rely on
CSS color inheritance in any state (including hover).
Save to `assets/images/svg/[descriptive-name].svg`
Replace with: `<img src="assets/images/svg/[name].svg" class="[original classes]" alt="[description]"/>`

Rules:
- When in doubt between B and C, always keep inline (choose B)
- Never use `<img>` for SVGs that change color on hover or via parent classes
- If the same SVG appears multiple times, classify once and apply consistently

---

## STEP 5 — WRITE design-system.html FROM SCRATCH

Using everything memorized in Step 1, write a new `design-system.html`
in the same folder as INPUT.

This is not a copy or edit of INPUT.
Write it clean, from scratch, section by section.

**`<head>` structure:**
```html
<head>
  <!-- fonts -->
  <link .../>

  <!-- css -->
  <!-- [what this file contains and where it is used] -->
  <link rel="stylesheet" href="assets/css/animations.css"/>

  <!-- head-only js (e.g. Tailwind runtime, must stay in head) -->
  <!-- [what this script does] -->
  <script src="assets/resource_xxx.js"></script>
</head>
```

**`<body>` structure:**
```html
<body>

  <!-- [section-id] -->
  ...section content...

  <!-- js -->
  <!-- [what this file does and where it is used] -->
  <script src="assets/js/interactions.js"></script>

</body>
```

**SVG rendering rules:**
- Category A (Lucide): `<i data-lucide="[name]" class="[classes]"></i>`
- Category B (currentColor): keep full SVG inline, minified to one line
- Category C (hardcoded): `<img src="assets/images/svg/[name].svg" .../>`

**Visual fidelity rules:**
- Every section from the original must be present
- Pixel-perfect reproduction: same layout, spacing, colors, and effects
- All animations, transitions, hover states, and decorative effects intact
- All existing asset paths (images, CSS, JS) preserved exactly as in INPUT
- Translate all visible text content to Brazilian Portuguese (PT-BR)
  This includes: headings, paragraphs, labels, buttons, nav items,
  badges, captions, and any other user-facing text
  Do NOT translate: code, class names, asset paths, or technical identifiers

**Compactness rules:**
- No blank lines or unnecessary whitespace
- No empty or redundant attributes
- No unused asset references
- Inline SVGs (Category B) minified to a single line each

---

## QUALITY BAR

Before saving, verify:
- [ ] Every section from the original is present and visually identical
- [ ] No inline `<style>` or `<script>` blocks remain
- [ ] All Lucide icons use `<i data-lucide>` — never `<img>` or inline SVG
- [ ] No currentColor SVG was moved to an `<img>` tag
- [ ] All extracted asset paths resolve correctly
- [ ] All imports in `<head>` and before `</body>` have descriptive comments
- [ ] No comments inside body other than section labels and asset imports
- [ ] All visible text has been translated to PT-BR
- [ ] File is meaningfully smaller and cleaner than INPUT

---

## STEP 6 — WRITE STACK.md

After design-system.html is saved, create a `STACK.md` file in the
same folder.

List every technology, library, and tool found in INPUT.
For each one, one line: name + what it does in this project.
No categories, no headers, no padding. Just the list.

Format:
- **Tailwind CSS** — utility-first CSS framework used for all layout and styling
- **Lucide** — icon library used throughout the interface

Only include what is actually present in the source.
Do not invent or assume technologies not found in INPUT.
