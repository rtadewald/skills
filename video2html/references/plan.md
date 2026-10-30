# The plan (Step 1)

The plan is a short message in the chat. The user must be able to read it and decide in about a minute.

## Format

```
**Plan — <name of the screen>**

Elements (back to front):
1. <element> — <category>: <how it will be built, one line>. <what moves / reacts, one line>
2. …

Phase 1: <element(s)> — <why it is the risky one>. (or: "none — everything is DOM/SVG")
Phase 2: the rest, in the fixed order (background → structure and fonts → components → icons → live layers →
Phase 1 piece → interactions → review).

Layers (back to front): <element numbers>
Ignore (video artefacts): <list>
```

Rules:

- One line per element. Group identical items ("12 agent nodes").
- Name the technology concretely (`SVG + GSAP`, `fbm shader`, `GLB from image-to-3D + Three.js`), not vaguely ("code").
- Say what moves and what reacts. Behaviour that the video does not show but that the element obviously has (a node
  that lights up on hover) goes here too.
- List the artefacts so nobody rebuilds them.

## Example

A 6-second video of a voice-assistant dashboard: a robot head in the middle, a rotating HUD behind it, telemetry on the
left, an arc of agent nodes on the right, a chat card on the far right.

```
**Plan — assistant dashboard**

Elements (back to front):
1. Background — Shader: dark navy radial gradient in CSS + a light fbm smoke shader around the center. The smoke drifts slowly.
2. HUD behind the head — DOM: concentric SVG rings, ticks and crosshair. Rings rotate slowly in opposite directions; an arc points at the cursor.
3. Robot head and shoulders — 3D model: GLB from image-to-3D, neck/head rig, Three.js. Looks at the cursor, turns to the agent being called, eye glows when it talks.
4. Robot glow — Shader: bloom on a second canvas, screen-blended. Pulses ~2 s, follows the voice.
5. Logo (top left) — DOM: text in the identified font (or SVG path if no font matches).
6. Clock (top right) — DOM: real time.
7. Telemetry (left: CPU, memory, network, tasks) — DOM: text + SVG sparklines/bars. Values tick slowly.
8. Agent arc with 12 nodes and connectors — DOM: SVG arc and lines, HTML nodes. A light travels to a node and lights it; hover lights it too.
9. Chat card (right) — DOM: glass panel, messages, real input. Built with care: it is the most unusual component.
10. Icons (telemetry, agents, avatars, chat buttons, mic) — DOM: inline SVG, one stroke style.

Phase 1: the robot (3) with its glow (4) — a 3D character is the riskiest piece.
Phase 2: the rest, in the fixed order.

Layers (back to front): 1 → 2 → 8 → 3 → 4 → 5, 6, 7, 9
Ignore (video artefacts): node labels that melt between 2.8 and 4.5 s; flicker on the robot's mesh.
```
