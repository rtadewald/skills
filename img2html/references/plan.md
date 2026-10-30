# The plan (Step 1)

A short message in the chat: the screen as layers from back to front, each with how it will be built. The user must be
able to read it and decide in about a minute.

## Format

```
**Plan — <name of the screen>** (<width>×<height>)

Layers, back to front:
1. <layer> — <technique>: <how, one line>
2. …

Fonts: <text style> → <family weight> (alternative: …)
Assets to generate: <list, or "none">
Interactions: <hover / focus / inputs / tabs>
```

Rules:

- One line per layer. Group identical items ("6 conversation rows").
- Name the technique concretely: `CSS radial gradient`, `CSS glass (blur 24px, 1px rim)`, `SVG polyline`, `image
  regenerated from a crop, transparent background`, `crop of the reference`.
- Text is always HTML: say which layer it belongs to, not "an image with text".
- Mention what is uncertain ("the logo may need an SVG path if no font matches").

## Example

A 1536×864 chat app: a studio background with glass and chrome objects, a glass sidebar on the left, a glass
conversation panel in the middle.

```
**Plan — NStreak chat (minimal)** (1536×864)

Layers, back to front:
1. Background scene (grey-blue studio, glass and chrome objects, warm bulbs) — image: the reference without the two
   panels, regenerated and re-aligned (align.py); the objects are art, not code.
2. Sidebar panel — CSS glass: rgba fill, backdrop blur, 1px bright rim, 24px radius.
3. Conversation panel — CSS glass, same tokens as the sidebar.
4. Sidebar content — HTML: logo text, search input, gradient "Nova conversa" pill (CSS gradient), 6 conversation rows,
   one active (soft glow), profile row with a cropped avatar.
5. Conversation content — HTML: header with title and menu dots, user bubble (glass), assistant answer with a numbered
   list, input bar with mic icon and gradient send button.
6. Icons (search, pencil, chat rows, mic, send, back, dots) — inline SVG, 1.5px stroke, rounded.

Fonts: logo and titles → Inter 500 · body → Inter 400 · input placeholder → Inter 400 (alternative: SF Pro if Inter is
too wide).
Assets to generate: the background plate (1).
Interactions: hover on conversation rows and buttons, focus ring on inputs, the input accepts text.
```
