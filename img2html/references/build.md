# Building the page (Step 2)

## The stage

Build the page on a fixed stage with the image's size, scaled to the window, so every measurement taken from the image
is used as it is:

```css
:root { --px: calc(100cqw / 1536); }              /* 1 --px = 1 px of the image (here 1536 wide) */
html, body { margin: 0; height: 100%; overflow: hidden; }
body { display: grid; place-items: center; }
.stage { position: relative; width: min(100vw, calc(100vh * 16 / 9)); aspect-ratio: 16 / 9;
  container-type: inline-size; overflow: hidden; }
.stage > * { position: absolute; }
.sidebar { left: calc(40 * var(--px)); top: calc(40 * var(--px)); width: calc(250 * var(--px)); }
```

Every element placed by the image's coordinates needs `position: absolute`; a wrapper left `static` breaks its group.
Content inside a panel can use normal flow (flex, grid) when that is simpler and stays faithful.

## Measure

Measure from the image instead of guessing:

- **Colors:** sample small areas (average a 12×12 box) at the background corners, the center, each surface fill, rims,
  text. With Python + Pillow: `img.crop(box).resize((1, 1), Image.BOX).getpixel((0, 0))`.
- **Gradients:** sample along a line and pick the stops where the color changes; for radial backgrounds, sample along a
  radius from the light's center.
- **Boxes:** find the bounding box of dark or bright pixels in a region (threshold + bounding box) to get exact text
  lines, panel edges and icon sizes.
- **Circles and arcs:** collect the centers of the items on the arc and fit a circle by least squares; if the residuals
  are large, draw a smooth curve through the points instead.
- **Repeated items:** keep their coordinates in one list (or generate the markup from one list) so a change is made once.

## Fonts

Fonts come before any fine-tuning of sizes:

```
uv run ~/.agents/skills/img2html/scripts/fonts.py reference.png review/fonts.png --box 52,40,210,72 --text "JARVIS" \
  --fonts "Inter,Manrope,Jost,Turret Road,Michroma" --size 24 --spacing 0.5em
```

It renders each candidate with the same text next to the crop of the image. Pick the closest shape (letter widths,
terminals, the shape of a, g, R, S), then set size and letter-spacing by measuring the ink box. If none matches (a custom
logo), draw the letters as an SVG path.

## Surfaces

For each panel or card, one at a time: crop the image, sample fill / rim / shadow colors, write the CSS, screenshot,
compare the crop, adjust. Typical values to get right: radius, border width and color, fill opacity, backdrop blur,
inner glow, outer shadow, padding.

Reuse values: when two surfaces share a look, they share the custom properties.

## Assets

When a layer is an image (a background scene, an illustration, a photo, a complex icon):

1. Crop the region of the reference into `assets/crops/<name>.png`.
2. Generate in parallel, one request per asset, with the `openrouter-img` skill:
   ```
   uv run ~/.agents/skills/openrouter-img/scripts/generate_image.py --prompt "…" --input-image assets/crops/<name>.png \
     --filename assets/<name>.png --model gpt2 --resolution 2K --aspect-ratio 16:9 &
   …
   wait
   ```
   - Backgrounds and plates: "the same scene without the panels / text / UI, same framing", never with UI text.
   - Icons and objects to cut out: "transparent background, no padding, no frame".
3. A plate that must sit exactly under the page goes back in place with
   `uv run ~/.agents/skills/img2html/scripts/align.py reference.png assets/<name>.png assets/<name>.png --mask x,y,w,h` (it finds the shift and
   scale that best match the reference, and keeps the reference's pixels outside the mask when given).
4. Only regenerate the assets that failed.

## The log (`steps.md`)

```
# Steps

- [x] 1 Stage and background — ok. review/01-background/side-by-side.jpg
- [x] 2 Surfaces — ok. sidebar 4.1/255, panel 3.8/255
- [x] 3 Fonts and text — difference: the logo is an SVG path (no font matches).
- [ ] 4 Components
…
```

## Final review

```
uv run ~/.agents/skills/video2html/scripts/snap.py http://localhost:8000/index.html review/final.png --shot --wait 3
uv run ~/.agents/skills/video2html/scripts/compare.py reference.png review/final.png review/final
```

Send `review/final/side-by-side.jpg`, the mean difference, and the remaining differences from `steps.md`.
