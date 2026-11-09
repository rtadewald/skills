---
name: draw-wireframe
description: Draws grayscale UI wireframes (dashboards, sites, apps) instantly and at no image-API cost, from a short layout file rendered by a script: raw skeletons with no text, or real text in a chosen font to test typography and copy placement. Use when the user mentions draw-wireframe or asks for a wireframe or skeleton of a screen, from a conversation, a brief or a reference image.
---

# Draw Wireframe

You write a short layout file (`.wf`); `scripts/draw.py` draws it. No image model is involved, so a wireframe costs only the few lines you write.

## Steps

1. **Decide the screen.** It can come from the conversation, a brief, a reference image, or your own proposal when the conversation leaves it open. Draw one wireframe or several options, as the conversation asks.
2. **Write `<name>.wf`** in the output folder, using the format below. Write the real text in the pieces even for a raw wireframe: it sets the length of the bars, and the same file then works in both modes.
3. **Run the script** (`uv run <this skill>/scripts/draw.py`):
   ```bash
   uv run scripts/draw.py a.wf [b.wf c.wf] --out DIR                  # raw: SVG + PNG, text becomes bars
   uv run scripts/draw.py a.wf --out DIR --text --font "Lexend"       # text: HTML + PNG, real text
   uv run scripts/draw.py a.wf --out DIR --text --font "Lexend,Sora"  # one file per font (any Google Font)
   uv run scripts/draw.py a.wf --out DIR --compare reference.png      # adds a side-by-side with a reference
   ```
   More than one output also writes `sheet.png`, with all of them side by side.
4. **Look at the PNG** and fix what overlaps or gets cut (text ending in "…" needs more room). Then show it.

**From a reference image:** read the image, write the layout, run with `--compare`, correct once if needed. The goal is the same skeleton, not pixel precision.

## Layout format

Indentation is the tree. Each line is `piece "text" "more text" key=value flag`; `#` starts a comment. The first line chooses the screen.

```
screen dashboard
col pad=20 gap=14
  row h=44 gap=8
    pill "Search" w=400 h=44 knob=right
    space
    dot size=44
  row gap=14
    card f=2
      title "Revenue" size=16
      bars n=12
    card
      kpi "R$ 90.235" "won this month"
      button "Export"
```

- **Screens:** `dashboard` (1440×900), `site` (1440 wide, the height grows with the sections, so give sections an `h=`), `app` (phone), or a free size such as `1200x800`. `margin=` sets the space around the panel.
- **Containers:** `row` and `col` have no surface; `card` is a surface (a column, or `dir=row`); `image` is a lighter surface. Any surface can hold pieces. `space` pushes what follows to the far end.
- **Sizes:** `w=` and `h=` are fixed pixels; `f=2` is a share of the free space along the parent (default 1). `pad=`, `gap=` and `r=` (corner radius) work on containers.
- Each nested surface is automatically one step lighter.

## Pieces

| Group | Pieces |
|---|---|
| Text | `title "…" size=28 center` · `text "…" size=14 muted center` (wraps) · `lines n=3 bold` (always bars) |
| Controls | `pill "…" knob=right\|left\|both solid` · `opill "…"` (outlined) · `button "…" ghost` · `input "…"` · `select "…"` · `toggle` · `tabs items="A\|B\|C" active=1` |
| Round | `dot size=36` · `dots n=5 size=36` · `avatars n=5 size=36` |
| Charts | `bars n=12 values="3,5,2" labels="J\|F\|M"` · `line` · `area` · `spark` (these three take `values=`) · `donut pct=54` · `funnel labels="A\|B\|C"` · `progress pct=60` |
| Data | `kpi "number" "label" delta="▲ 12%" size=30` · `table cols="A\|B" rows=6 data="a,b\|c,d"` · `list items="A\|B"` or `n=4` · `calendar today=17` · `kanban cols="A\|B\|C" cards=3` |
| Sites and apps | `navbar "Brand" links="A\|B" cta="Start"` · `sidebar items="A\|B"` or `n=8` · `hero "Title" "Subtitle" cta="…"` · `cardgrid n=6 cols=3 items="A\|B"` · `footer cols=4` · `tabbar n=5 active=1` · `fan` (stacked cards) · `divider` |

A piece with no text draws neutral bars, in both modes. See `examples/` for a dashboard, a landing page and a phone screen.

## Modes

- **Raw:** the skeleton only, in the fixed style: grainy gray page, dark rounded panel, surfaces in steps of gray.
- **Text:** the same skeleton and the same grays, with real text in the chosen font, to judge typography and where the copy goes. It stays monochrome on purpose.

The PNG is what goes to other tools, such as an image model as a layout reference.
