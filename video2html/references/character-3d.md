# Phase 1 recipe: a 3D character from the image

Goal: a rigged GLB that **matches the image in its resting pose**, animated in Three.js (looks at the cursor, talks,
breathes), shown in place on `phase1/index.html`.

Work in `phase1/`. Every script below is in `scripts/` and runs with `uv run` (Blender scripts with `blender -b -P`).

## 1. A clean image of the character

Image-to-3D models need the subject alone, whole, evenly lit, on a plain background.

```
uv run scripts/isolate_subject.py reference.png phase1/subject.png \
  --describe "the cybernetic android head-and-shoulders bust, one round glowing cyan eye on the right side of the face, cyan light strips along the cheek"
```

- `--describe` must name the **distinctive details** (number of eyes, asymmetries, light strips). Models simplify what
  is not named: a one-eyed robot becomes two-eyed.
- Keep the **view of the image** (e.g. three-quarters). The default prompt asks for it; check the result.
- Look at `subject.png` before spending on 3D. If a detail is wrong, fix `--describe` and run again (cents).

## 2. Image-to-3D, several models in parallel

```
uv run scripts/image_to_3d.py phase1/subject.png phase1/models --models tripo,trellis2,rodin
```

- Runs on fal.ai (`FAL_KEY`). About US$ 0.30–0.40 per model; 1–3 minutes each. Writes `<model>.glb` and `<model>.json`.
- Available: `tripo` (Tripo H3.1, best textures in our tests), `trellis2`, `rodin`, `hunyuan`. `--models all` runs all four.

## 3. Pick the closest to the image

```
blender -b -P scripts/render_views.py -- phase1/models/tripo.glb phase1/models/tripo --rotate -90 --yaw -35
```

- Renders front, side, back and a **view at `--yaw` degrees**: use the character's angle in the image (e.g. `--yaw -35`
  for a three-quarters view; if it turns the wrong way, flip the sign).
- Models disagree on the front axis. Render once without `--rotate`; if "front" shows a side or the back, try `--rotate
  -90`, `90` or `180` (it turns the model). Use the same value later in `rig_bust.py`. Tripo models usually need `-90`.
- Put each model's yaw view next to the character's crop from the image and choose the closest **in design and
  details**, not the prettiest. Write the choice and why in `phase1/notes.md`.
- If none is close: improve `subject.png` (step 1) and run step 2 again.

## 4. Prepare and rig (Blender)

```
uv run scripts/extract_emissive.py phase1/models/tripo.glb phase1/work --hue cyan
blender -b -P scripts/rig_bust.py -- phase1/models/tripo.glb phase1/work/emissive.png phase1/character.glb --rotate -90
```

- `extract_emissive.py` pulls the textures out of the GLB and builds an **emissive mask** from the glowing color
  (cyan/blue by default): those texels will glow and react to the voice. Check `work/emissive-preview.png`.
- `rig_bust.py` (for a head-and-shoulders bust):
  - fixes orientation (`--rotate` in degrees, so the front faces +Z in glTF);
  - normalizes size (2 units tall, base at 0);
  - reduces to ~120k triangles;
  - finds the neck (the narrowest slice);
  - builds the bones `bust → neck → head`;
  - weights the head with an ellipsoid fitted to it, so the chin goes with the head and the shoulders stay still;
  - plugs the emissive mask in;
  - exports with WebP textures.
- Check the rig with `blender -b -P scripts/render_views.py -- phase1/character.glb phase1/work/rig --pose` (renders
  the head turned left, right and down). The face must not smear and the shoulders must not move.
- For a full body or a creature, `rig_bust.py` is a starting point only: adapt the bone chain and the weights.

## 5. The page

Copy [../templates/character.html](../templates/character.html) to `phase1/index.html`, the GLB next to it, and set
the constants at the top:

- `STAGE`: the image size (e.g. 1536×864);
- `HEAD_AT`: where the camera puts the aim point, in image pixels;
- `CAM_Z`: the camera distance, which sets the size;
- `FADE`: where the bottom of the bust fades out;
- `REFERENCE`: the image shown behind it, dimmed (key `R` toggles it);
- `MODEL_YAW`: the resting turn of the model in degrees, so it rests in the image's view (the `--yaw` that matched in
  step 3; flip the sign if it turns the wrong way). Looking at the cursor is measured from this rest;
- `GLOW`, `GLOW_TINT`, `BLOOM`: strength and color of the glowing parts and of the bloom. Generated textures often
  glow teal or too strong: tint toward the image's glow color and lower the strength;
- `ENV`: environment reflections; lower it when black glossy parts (visors, screens) look grey.
- `BACKDROP`: the page color, dark or light like the scene.
- `FLOAT`: for a floating character, the bob height, its period and a small sway.
- `LIGHTS`: key, rim and back light. A purple back light shows on dark armor; keep the colors close to the image's.

When the template improves later, `uv run scripts/apply_template.py phase1/index.html` updates the page and keeps its
settings.

Fit it: screenshot (`snap.py`), compare with the image (`compare.py`), adjust the three constants until eyes, head
top and shoulders sit where they are in the image.

What the template already does:

- **Looks at the cursor:** the head and neck turn toward the cursor, projected on a plane in front of the face, with
  limits (yaw ±0.6, pitch ±0.35 rad), split 35% neck / 65% head.
- **Idle:** a slow drift, micro-breathing, blinking of the glow.
- **Talks:** click on the character plays a voice file; an `AnalyserNode` volume envelope drives the emissive
  intensity, and each syllable (fast rise above the slow envelope) nods the head. Voice files: macOS
  `say -v "<voice>" -o f1.aiff "<text>" && ffmpeg -i f1.aiff f1.mp3`, or any TTS.
- **Glow:** emissive parts rendered again on a second canvas through bloom and screen-blended on top. This keeps the
  main canvas transparent.
- **Hooks for Phase 2:** `window.character.lookAt(x, y, ms)` makes it look at a point (e.g. the agent being called);
  `window.character.say(n)` plays voice `n`.

## 6. Approval

Show `phase1/index.html` with a screenshot next to the image. Ask: right model? right fit? right motion? **Stop.**
