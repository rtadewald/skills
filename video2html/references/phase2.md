# Phase 2: everything else, autonomously

The agent builds the rest of the screen alone, step by step, reviewing each step against the image. The user sees
only the final result.

## Before the first step

1. **Stage.** Build the page on a fixed stage with the image's size, scaled to the window, so measurements from the
   image are used as they are. With CSS only:

   ```css
   :root { --px: calc(100cqw / 1536); }          /* 1 --px = 1 px of the image */
   body { margin: 0; height: 100vh; display: grid; place-items: center; overflow: hidden; }
   .stage { position: relative; width: min(100vw, calc(100vh * 16 / 9)); aspect-ratio: 16 / 9; container-type: inline-size; overflow: hidden; }
   .stage > * { position: absolute; }
   .logo { left: calc(53 * var(--px)); top: calc(47 * var(--px)); font-size: calc(18 * var(--px)); }
   ```

   Every element that must follow the image's coordinates needs `position: absolute`. A parent left `static` breaks
   the whole group.

2. **Layers.** Create the layers in the order of the plan, back to front. Every WebGL canvas gets
   `pointer-events: none` so the DOM under it stays clickable.

3. **Log.** Create `steps.md` with the eight steps below as a checklist.

## The eight steps

| # | Step | Done when |
|---|---|---|
| 1 | **Background**: colors, gradients, base texture | sampled colors at 6–8 points match within a few levels |
| 2 | **Structure and texts, with fonts**: every block placed, every text real; family and weight identified first | text ink boxes within ±2 px |
| 3 | **Components**: logo, charts, cards, panels, nodes, one at a time, still static | each crop side by side looks the same |
| 4 | **Icons**: all in one go, inline SVG, one stroke style (a sprite of `<symbol>` + `<use>`) | no placeholder left |
| 5 | **Light live layers**: animated SVG, shaders, particles | their motion reads like the video |
| 6 | **Plug in the Phase 1 piece**: same constants as the approved page, at its layer | screenshot matches the approved fit |
| 7 | **Interactions and motion**: the video's events, hover/click states, the idle loop | a recording reads like the video; hovers react |
| 8 | **Final review**: full screenshot vs image; recording vs video | differences listed |

Measurement and technique details per category: [categories.md](categories.md).

## The review loop (every step)

```
uv run scripts/snap.py http://localhost:8000/index.html review/03-chat.png --shot --wait 3
uv run scripts/compare.py reference.png review/03-chat.png review/03-chat --regions "chat:1215,240,285,375"
```

- Look at `review/03-chat/zoom-chat.jpg` (image | page) and read the mean difference.
- Fix, repeat. **At most 3 rounds per step.** If something still differs, log it and move on.
- For motion (steps 5 and 7), record and compare against the video:
  ```
  uv run scripts/snap.py http://localhost:8000/index.html review/motion.mp4 --seconds 6
  uv run scripts/describe_motion.py analysis/video.mp4 review/motion.md --compare review/motion.mp4
  ```
  The description model misses short events: check frames before changing the page because of it.

## The log (`steps.md`)

```
# Steps

- [x] 1 Background — ok. review/01-background/side-by-side.jpg
- [x] 2 Structure and fonts — difference: the clock's "4" is open in the font (Turret Road), closed in the image.
- [x] 3 Components — ok. review/03-*/
- [ ] 4 Icons
…
```

## Final delivery

Send the user:

- the page URL;
- `review/final/side-by-side.jpg` (image | page, full screen);
- a short recording (`review/final.mp4`);
- the remaining differences from `steps.md`.

Ask for approval and **stop**.
