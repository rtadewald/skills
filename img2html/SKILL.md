---
name: img2html
description: >-
  Recreates a UI mock (a still image) as a faithful static HTML page in one go: a short plan of the screen's layers from
  back to front, approved by the user, then the whole page built autonomously with self-review against the image, then a
  final approval. No wireframe, two approval points. Use when the user mentions img2html.
---

# Img → HTML (one pass)

## What this skill does

**Input:** one image of an app or site screen (path, attachment or URL). If it is missing, ask for it.

**Output:** a folder with `index.html` and `assets/` (CSS, JS, generated images) that looks like the image, with real
text, real inputs and simple hover states, at the proportions of a normal dashboard (see [Scale](#scale)).

**How:** decide everything first, as layers from back to front, and agree on it with the user. Then build the whole page
without stopping, checking each step against the image yourself. The user is asked **twice**: the plan, and the result.

## The process at a glance

```
1. Plan     read the image → its layers from back to front, each with how it will be built, fonts, assets → [user approves]
2. Build    the whole page, in a fixed order, each step self-reviewed (max 3 rounds), logged in steps.md
3. Deliver  the page, a side-by-side with the image, and the differences that remain                → [user approves]
```

At each approval point: show (path + screenshot), ask, and **stop**. Continue only on an explicit "ok" / "approved" /
"go on". If the user asks for changes, make them, show again, wait again.

**The project's own rules come first.** If the folder you work in has an `AGENTS.md` (or `CLAUDE.md`) with its own way to
start the work, report progress, register generated files or show a page for approval, read it before Step 1 and
follow it at every step and at every approval point, in addition to this skill.

---

## Step 1 — Plan, from back to front

1. Create the output folder (the user's choice, or `img2html/<slug>/` in the working directory) and copy the image to
   `reference.png`.
2. Look at the image at full size, region by region. Measure what you can (see
   [references/build.md](references/build.md#measure)).
3. Write the plan in the chat, in the format of [references/plan.md](references/plan.md):
   - **layers from back to front**, one line each: *what it is → how it will be built*. The usual order is background →
     large surfaces (panels, cards, sidebars) → components inside them → text → icons and small graphics → anything that
     floats on top;
   - for each layer, the technique: **CSS** (colors, gradients, borders, glass), **SVG** (lines, charts, icons, logos),
     **image** (a crop of the reference, or an image regenerated from a crop) or a **mix**;
   - the **fonts**: family and weight per text style, with the alternative if no font matches;
   - the **scale**: the body text size measured in the image (converted to a 1536 px wide stage) and the factor that
     brings it into the [size table](#scale), plus what will fill the room it frees;
   - the **assets** to generate (backgrounds, illustrations, photos, icons that are not simple strokes);
   - the **interactions** that the screen obviously has (hover, focus, a real input, a clickable tab).
4. **Stop for approval.**

Rules for the plan:

- Short: the user must be able to judge it in a minute.
- Every visible thing belongs to a layer, including the background and the icons.
- Text and controls are always HTML, never part of an image.
- Choose by fidelity and by how easy it will be to adjust later: simple shapes and colors in CSS, art and textures as
  images, separate layers when they must move or be adjusted independently.

## Step 2 — Build, in one go

Follow the order below. Skip a step only when the plan has nothing for it. Details for each step:
[references/build.md](references/build.md).

1. **Stage and background.** The page is a fixed stage with the image's size, scaled to the window (1 unit = 1 pixel
   of the image). Background in CSS, or the generated background plate.
2. **Large surfaces.** Panels, sidebars, cards: position, size, radius, border, fill, blur, shadow. Positions come from
   the image; what goes inside them is sized by the [size table](#scale), and the panels keep filling the stage.
3. **Fonts and text.** Identify family and weight first (`fonts.py`), then place every text with its real content, at the
   sizes of the table, not the sizes measured in the image.
4. **Components.** Buttons, inputs, lists, charts, avatars, one surface at a time, from the back.
5. **Icons and assets.** Inline SVG for stroke icons (one style for all); generated images for everything else
   (`generate_image.py` from the `openrouter-img` skill, then `align.py` when an image must sit exactly in place).
6. **Interactions.** Hover and focus states, real inputs, the obvious clickable things. Small CSS transitions only.
7. **Final review.** A full screenshot next to the image.

**Self-review at the end of every step:**

1. Screenshot: `uv run ~/.agents/skills/video2html/scripts/snap.py <url> review/<step>.png --shot`
2. Compare the region of the step with the same crop of the image:
   `uv run ~/.agents/skills/video2html/scripts/compare.py reference.png review/<step>.png review/<step> --regions "name:x,y,w,h"`
   Smaller text and controls, and the extra rows that fill the room, are intended differences: judge colors, materials,
   composition and the order of elements, not the size of each piece.
3. Fix and repeat, **at most 3 rounds**. If something still differs, write it down and move on.
4. Log the step in `steps.md`: the side-by-side and one line, `ok` or `difference: …`.

(The scripts live in the sibling `video2html` skill: `~/.agents/skills/video2html/scripts/`.)

## Step 3 — Deliver

Send the page URL, `review/final/side-by-side.jpg` (image | page), the body size before → after, and the remaining
differences from `steps.md`. **Stop for approval.**

---

## Scale

Image models draw UI too large: copying the image's proportions gives giant type, chunky buttons and half-empty panels.
The page keeps the image's look and composition, but its type and controls follow this table, measured on a stage
1536 px wide (for another width, multiply by width ÷ 1536):

| Element | Size |
|---|---|
| Body, list items, table cells, chat bubbles | 13 to 14.5 px |
| Secondary text, labels, metadata | 11 to 12.5 px (never below 11) |
| Tabs and navigation | 12 to 13.5 px |
| Panel title | 17 to 20 px |
| Numbers inside a panel (KPI, multiplier) | 22 to 28 px |
| The page's highlight number | up to 64 px |
| The page's main title | up to 48 to 56 px |
| List row | 44 to 60 px high |
| Compact table row | at least 28 px high |
| Button, field, pill | 30 to 38 px high |
| Avatar | 28 to 40 px |
| Logo | up to 26 px |

- **Measure first.** In Step 1, measure the body text of the image (the x-height or cap height of a list or a table,
  converted to font size) and pick one factor, usually 13.5 ÷ that size. If the body is already 13 to 14.5 px, change
  only what falls outside the table.
- **Scale everything with it,** not only the type: paddings, gaps, radii, icons, avatars, thumbnails, chart labels.
  Hairlines of 1 to 2 px stay as they are.
- **Fill the room it frees.** The panels keep the positions and sizes of the image and occupy the stage, with outer
  margins of 38 to 50 px and gaps of 14 to 20 px. Fill, in this order: more rows in the same pattern (a list, a table, a
  chat), wider columns or taller blocks, and only as a last resort a new block in the page's style. At most 7 rows in a
  list and 4 to 6 messages in a chat (an empty stretch between the messages and the input is normal). Prefer widening
  columns to stacking content. New text follows the existing pattern (short labels, Lorem Ipsum for prose).
- **Identity exception.** When giant type is the direction of the screen (a poster-like title, a huge number that is the
  whole point), that one element may stay well above the table. Say so in the plan. Everything else follows the table.

---

## Folder layout

```
<output>/
  reference.png       the image (the only source of truth)
  index.html          markup only: no <style>, no <script> inline, no style="…"
  assets/
    styles.css        all CSS, design tokens as custom properties in :root
    app.js            only if the page needs behavior
    crops/            crops of the reference used as inputs for generated assets
    *.png / *.svg     generated images and icons
  review/             screenshots and comparisons, one folder per step
  steps.md            the build log
```

**Stack:** plain HTML + CSS (+ JS only if needed), no build step, no framework. Google Fonts are allowed; other libraries
only if the user asks. Serve the folder over `http://` to review it (`python3 -m http.server`).

## Keys and tools

- `OPENROUTER_API_KEY` (generated assets): from the environment, `./.env` or `~/.env`. Never print it.
- `uv` runs every script. Google Chrome for headless screenshots.
- Scripts here: `fonts.py` (compare candidate fonts with a crop of the text), `align.py` (put a generated image back
  in place over the reference). From `video2html/scripts/`: `snap.py`, `compare.py`.

## Pitfalls

- **Every element that follows the image's coordinates needs `position: absolute`.** A wrapper left `static` sends a
  whole group to the top-left corner.
- **Image models move and resize what they edit.** A generated background or plate must be re-aligned to the reference
  (`align.py`), and outside the edited area the reference's own pixels should be kept.
- **Image models invent text.** Never let a generated image contain UI text: ask for the art only.
- **Do not name known brands or characters** in image prompts: the safety filter rejects them. Describe shapes and
  materials.
- **Fonts first.** Sizes, line breaks and spacing only make sense once the family and weight are right.
- **A logo with unusual letter shapes** (no crossbar on the A, an S drawn like a Z) has no font: draw it as an SVG path.
