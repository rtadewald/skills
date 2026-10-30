# Pitfalls

Mistakes that already cost time. Read before Phase 1.

## Process

- **Do not guess what the video shows.** Check frames before putting an effect in the plan. An effect described in the
  prompt that generated the video may not be in the video at all.
- **Every moving element belongs in the plan.** A rotating HUD drawn as "static, with a note" ends up baked into a
  flat image and cannot rotate later.
- **Decide layer order in the plan.** A HUD meant to sit behind a character, drawn on a layer in front of it, crosses
  the face.

## Image models

- **Edits move and resize the subject.** Asked to isolate or remove something, GPT Image–class models often shift the
  subject by tens or hundreds of pixels and scale it a few percent. Always re-align the output to the reference (phase
  correlation for the shift, then a small scale/shift search), and keep the reference's pixels outside the edited mask.
- **Models simplify what you do not name.** List the distinctive details in the prompt.
- **Do not name known characters or brands** ("EVE-like", "Iron Man helmet"): the safety filter rejects the request.
  Describe shapes, materials and colors instead.

## Blender

- **The glTF importer uses quaternions.** Setting `rotation_euler` on an imported object does nothing. Transform the
  mesh data instead: `obj.data.transform(Matrix.Rotation(angle, 4, 'Z'))`.
- **Image-to-3D models disagree on the front axis.** Render first, then rotate.
- **The first texture is not always the base color** (Rodin puts the normal map first). Find it through the material;
  `extract_emissive.py` does.
- **An arm pivot taken from the arm itself comes loose.** The top of an arm piece is often a cap curving over the joint;
  rotating around it lifts the arm away from the body. Pivot at the joint on the body (the outermost body points next
  to the arm's top), as `rig_bust.py --arms` does.
- **Body panels can be classified as arm.** A back plate that reaches out behind the shoulder has its center far to the
  side too; when the arm rises it leaves a hole in the back. `rig_bust.py --arms` keeps a piece in the arm only if it is
  far to the side as a whole (10th percentile of its side distance). Check with a render that colors the arm.
- **Pointing in the screen plane looks like flapping.** Turn the arm in 3D toward the target on a plane a little in front
  of the body (`ARMS.depth`); keep the turn limited (`ARMS.reach`) so rigid pieces do not show gaps.
- **Head weights by height alone smear the face:** the chin stays with the neck. Use an ellipsoid fitted to the head
  plus a slanted boundary in front of the neck. Check by rendering turned poses.

## Three.js and shaders

- **A hidden tab pauses `requestAnimationFrame`.** An animation that "doesn't work" in a background tab may be fine.
  Verify with `snap.py` (headless Chrome).
- **Bloom erases alpha.** `UnrealBloomPass` makes the canvas opaque. Render the object on a transparent canvas and the
  glow on a second canvas (black background, only the bright parts), blended with `mix-blend-mode: screen`.
- **`ShaderMaterial` colors are linear.** With `OutputPass` (sRGB output), a color picked from the image must be
  converted (`pow(c, 2.2)`), or it comes out washed.
- **A character resting turned (MODEL_YAW) needs the head rotations in the model's frame**, or "look down" tilts the
  head diagonally. The template does it: D = M · E · M⁻¹.
- **Premultiplied alpha** for cut-outs: `gl_FragColor = vec4(rgb * a, a)`, or the cut-out shows as a rectangle.
- **Numbers in GLSL templates:** `${x}.0` becomes `616.5.0` when `x` already has decimals. Use
  `const f = v => Number.isInteger(v) ? v + '.0' : String(v)`.
- **`THREE.Points` without `position`:** a vertex shader that ignores `position` may draw nothing (Chrome/ANGLE).
  Add `position.xy` even if it is zero.
- **`.glb` from some hosts** is refused or mis-typed. Serve the folder locally over http; if a host refuses `.glb`,
  ship the glTF as JSON and rebuild the binary in memory.

## GSAP and SVG

- Do not set `transform-box` / `transform-origin` in CSS on SVG elements that GSAP scales or rotates: use `svgOrigin`.
- Kill the previous tween on the same element before starting a new one (`gsap.killTweensOf`), or they pile up.
- An idle timeline must reset its state at time 0: what it turned on midway, it turns off.

## Recording and review

- `page.evaluate` returning a GSAP object hangs Playwright; `snap.py --before` already wraps the JS.
- A JavaScript error stops everything after it. Read the page errors that `snap.py` prints.
- Do not serve code with a long cache, or the browser keeps running the old version.
