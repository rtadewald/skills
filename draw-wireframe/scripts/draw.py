# /// script
# requires-python = ">=3.11"
# dependencies = ["playwright"]
# ///
"""Draw grayscale UI wireframes from a short layout file. No image API: cheap and instant.

    uv run draw.py a.wf [b.wf …] --out DIR                 raw mode: SVG + PNG, no text (text becomes bars)
    uv run draw.py a.wf --out DIR --text --font "Lexend"   text mode: HTML + PNG with real text
    uv run draw.py a.wf --out DIR --text --font "Lexend,Inter,Sora"   one file per font, plus a sheet
    uv run draw.py a.wf --out DIR --compare ref.png        also writes a side-by-side with a reference image

More than one output also writes sheet.png (all of them side by side). Layout format: see SKILL.md.
"""
from __future__ import annotations

import argparse
import html
import math
import re
import shlex
from pathlib import Path

SCREENS = {'dashboard': (1440, 900, 56), 'site': (1440, 0, 56), 'app': (430, 900, 24)}
PAGE, GRAIN = '#bdbdbd', 0.09
TONES = ['#333333', '#474747', '#5c5c5c', '#6e6e6e', '#7e7e7e']   # the panel and each nested card, one step lighter
FG, FG2, LIGHT = '#8e8e8e', '#767676', '#b4b4b4'                   # text bars, secondary bars, solid elements
INK, INK2, DARK = '#ececec', '#b9b9b9', '#1c1c1c'                  # real text
PLAIN = {'row', 'col', 'space'}                                    # containers without a surface


class Node:
    def __init__(self, kind, args, opts):
        self.kind, self.args, self.opts, self.kids = kind, args, opts, []
        self.box = (0, 0, 0, 0)

    def num(self, key, default=None):
        v = self.opts.get(key)
        return default if v is None else float(v)

    def items(self, key='items'):
        v = self.opts.get(key)
        return v.split('|') if v else []

    @property
    def horizontal(self):
        return self.kind == 'row' or self.opts.get('dir') == 'row'

    @property
    def pad(self):
        return self.num('pad', 0 if self.kind in PLAIN else 16)

    @property
    def gap(self):
        return self.num('gap', 12)


def parse(path):
    """Indentation is the tree. Each line: kind "text" "more text" key=value flag."""
    root, stack, screen = None, [], ('dashboard', {})
    for raw in Path(path).read_text(encoding='utf-8').splitlines():
        if not raw.strip() or raw.lstrip().startswith('#'):
            continue
        indent, toks = len(raw) - len(raw.lstrip()), shlex.split(raw.strip())
        args, opts = [], {}
        for t in toks[1:]:
            if re.fullmatch(r'[a-z]+=.*', t):
                k, v = t.split('=', 1); opts[k] = v
            elif re.fullmatch(r'[a-z]+', t) and t in ('solid', 'ghost', 'bold', 'center', 'muted', 'end'):
                opts[t] = '1'
            else:
                args.append(t)
        if toks[0] == 'screen':
            screen = (args[0] if args else 'dashboard', opts)
            continue
        node = Node(toks[0], args, opts)
        while stack and stack[-1][0] >= indent:
            stack.pop()
        if stack:
            stack[-1][1].kids.append(node)
        elif root is None:
            root = node
        else:
            raise SystemExit(f'{path}: only one top-level element is allowed (wrap them in a col)')
        stack.append((indent, node))
    if root is None:
        raise SystemExit(f'{path}: empty layout')
    return screen, root


def chars(s, size):
    return len(s) * size * 0.54


# ---------- natural sizes (a piece with no size given takes these) ----------
NAT_H = {'text': 20, 'lines': 0, 'pill': 40, 'opill': 26, 'button': 44, 'input': 46, 'select': 46, 'toggle': 26, 'kpi': 74, 'tabs': 42, 'navbar': 64,
         'footer': 180, 'tabbar': 68, 'divider': 1, 'progress': 10, 'hero': 460, 'image': 240, 'bars': 220, 'line': 220, 'area': 220, 'donut': 200,
         'funnel': 220, 'spark': 40, 'calendar': 250, 'kanban': 460, 'fan': 120, 'sidebar': 400}
NAT_W = {'opill': 96, 'toggle': 48, 'sidebar': 56}


def nat_h(n):
    if 'h' in n.opts:
        return n.num('h')
    if n.kind == 'title':
        return n.num('size', 28) * 1.3
    if n.kind == 'lines':
        return n.num('n', 3) * 20 - 6
    if n.kind in ('dot', 'dots', 'avatars'):
        return n.num('size', 36)
    if n.kind == 'list':
        return (len(n.items()) or n.num('n', 4)) * 48
    if n.kind == 'table':
        return (n.num('rows', 6) + 1) * 40
    if n.kind == 'cardgrid':
        return math.ceil(n.num('n', 6) / n.num('cols', 3)) * 260
    if n.kids:
        hs = [nat_h(k) for k in n.kids if k.kind != 'space']
        body = max(hs, default=0) if n.horizontal else sum(hs) + n.gap * (len(n.kids) - 1)
        return body + 2 * n.pad
    return NAT_H.get(n.kind, 120 if n.kind not in ('space',) else 0)


def nat_w(n):
    """A fixed width along a row, or None to share the free space."""
    if 'w' in n.opts:
        return n.num('w')
    if n.kind in ('dot',):
        return n.num('size', 36)
    if n.kind == 'dots':
        c = n.num('n', 5); return c * n.num('size', 36) + (c - 1) * 6
    if n.kind == 'avatars':
        c, s = n.num('n', 5), n.num('size', 36); return s + (c - 1) * s * 0.68
    if n.kind in ('pill', 'button') and 'f' not in n.opts:
        t = n.args[0] if n.args else ''
        return max(chars(t, 14) + 44, 110) + (36 if 'knob' in n.opts else 0)
    if n.kind == 'title' or n.kind == 'text':
        return None if 'f' in n.opts or not n.args else chars(n.args[0], n.num('size', 28 if n.kind == 'title' else 14)) * 1.2 + 8
    if n.kind in NAT_W and 'f' not in n.opts:
        return NAT_W[n.kind]
    return None


FLEX_H = {'card', 'row', 'col', 'space', 'image', 'bars', 'line', 'area', 'donut', 'funnel', 'calendar', 'kanban', 'fan', 'hero', 'table', 'cardgrid', 'sidebar', 'list'}


def layout(n, x, y, w, h):
    n.box = (x, y, w, h)
    if not n.kids:
        return
    p, g = n.pad, n.gap
    x, y, w, h = x + p, y + p, w - 2 * p, h - 2 * p
    horiz, total = n.horizontal, w if n.horizontal else h
    sizes, flex = [], 0.0
    for k in n.kids:
        if horiz:
            s = nat_w(k)
        else:
            s = k.num('h') if 'h' in k.opts else (None if 'f' in k.opts or k.kind in FLEX_H else nat_h(k))
        sizes.append(s)
        if s is None:
            flex += k.num('f', 1)
    free = max(0, total - sum(s or 0 for s in sizes) - g * (len(n.kids) - 1))
    pos = 0.0
    for k, s in zip(n.kids, sizes):
        size = s if s is not None else free * k.num('f', 1) / (flex or 1)
        if horiz:
            ch = min(h, k.num('h')) if 'h' in k.opts else (min(h, nat_h(k)) if k.kind in ('dot', 'dots', 'avatars', 'pill', 'opill', 'button', 'toggle', 'title', 'text') else h)
            layout(k, x + pos, y + (h - ch) / 2, size, ch)
        else:
            cw = min(w, k.num('w')) if 'w' in k.opts else w
            layout(k, x, y + pos, cw, size)
        pos += size + g


# ---------- drawing ----------
class Canvas:
    def __init__(self, text_mode, font):
        self.text_mode, self.font, self.out = text_mode, font, []

    def rect(self, x, y, w, h, r=0, fill='none', stroke=None, sw=1, op=None):
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
        o = f' opacity="{op}"' if op is not None else ''
        self.out.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{max(w, 0):.1f}" height="{max(h, 0):.1f}" rx="{min(r, h / 2, w / 2):.1f}" fill="{fill}"{s}{o}/>')

    def circle(self, x, y, r, fill='none', stroke=None, sw=1):
        s = f' stroke="{stroke}" stroke-width="{sw}"' if stroke else ''
        self.out.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r:.1f}" fill="{fill}"{s}/>')

    def path(self, d, fill='none', stroke=None, sw=2, op=None):
        s = f' stroke="{stroke}" stroke-width="{sw}" stroke-linecap="round" stroke-linejoin="round"' if stroke else ''
        o = f' opacity="{op}"' if op is not None else ''
        self.out.append(f'<path d="{d}" fill="{fill}"{s}{o}/>')

    def label(self, x, cy, s, size=14, weight=400, ink=INK, bar=FG, anchor='start', maxw=None):
        """Real text in text mode; otherwise a rounded bar as long as the text would be."""
        if not s:
            return
        wid = chars(s, size) * (1 if weight < 500 else 1.04)
        if maxw and wid > maxw:
            if self.text_mode:
                s = s[:max(1, int(len(s) * maxw / wid) - 1)] + '…'
            wid = maxw
        if self.text_mode:
            self.out.append(f'<text x="{x:.1f}" y="{cy:.1f}" font-size="{size:.1f}" font-weight="{weight}" fill="{ink}" text-anchor="{anchor}" dominant-baseline="central">{html.escape(s)}</text>')
        else:
            h = max(5, size * 0.62)
            bx = x - wid / 2 if anchor == 'middle' else x - wid if anchor == 'end' else x
            self.rect(bx, cy - h / 2, wid, h, h / 2, bar)


def wrap(s, size, w):
    out, cur = [], ''
    for word in s.split():
        if chars(cur + ' ' + word, size) > w and cur:
            out.append(cur); cur = word
        else:
            cur = (cur + ' ' + word).strip()
    return out + ([cur] if cur else [])


def draw(c, n, depth):
    x, y, w, h = n.box
    kind = n.kind
    tone = TONES[min(depth + 1, len(TONES) - 1)]     # a surface one step lighter than where it sits
    if kind not in PLAIN:
        fn = PIECES.get(kind)
        if fn is None:
            raise SystemExit(f'unknown piece: {kind}')
        fn(c, n, x, y, w, h, depth, tone)
    inner = depth + (0 if kind in PLAIN else 2 if kind == 'image' else 1)   # an image is two steps lighter than where it sits
    for k in n.kids:
        draw(c, k, inner)


def p_card(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, h, n.num('r', 22), tone)


def p_image(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, h, n.num('r', 20), TONES[min(d + 2, 4)])


def p_title(c, n, x, y, w, h, d, tone):
    size = n.num('size', 28); t = n.args[0] if n.args else 'Título da seção'
    a = 'middle' if 'center' in n.opts else 'start'
    c.label(x + w / 2 if a == 'middle' else x, y + h / 2, t, size, 600 if size < 40 else 500, anchor=a, bar=LIGHT if size >= 22 else FG, maxw=w)


def p_text(c, n, x, y, w, h, d, tone):
    size = n.num('size', 14); t = n.args[0] if n.args else 'Texto de apoio'
    rows = wrap(t, size, w); lh = size * 1.45
    start = y + (h - lh * len(rows)) / 2 + lh / 2
    a = 'middle' if 'center' in n.opts else 'start'
    for i, r in enumerate(rows):
        c.label(x + w / 2 if a == 'middle' else x, start + i * lh, r, size, ink=INK2 if 'muted' in n.opts else INK, bar=FG2 if 'muted' in n.opts else FG, anchor=a, maxw=w)


def p_lines(c, n, x, y, w, h, d, tone):
    k = int(n.num('n', 3)); first = 'bold' in n.opts
    for i in range(k):
        bw = w * (0.86 if first and i == 0 else [0.72, 0.5, 0.62, 0.42][i % 4])
        bh = 18 if first and i == 0 else 10
        c.rect(x, y + i * 20 + (0 if i == 0 or not first else 4), bw, bh, bh / 2, LIGHT if first and i == 0 else FG)


def p_pill(c, n, x, y, w, h, d, tone):
    solid = 'solid' in n.opts
    c.rect(x, y, w, h, h / 2, LIGHT if solid else tone)
    knob = n.opts.get('knob'); r = h / 2 - 3
    t = n.args[0] if n.args else ''
    if knob in ('right', 'both', '1'):
        c.circle(x + w - h / 2, y + h / 2, r, LIGHT if d >= 1 else FG)
    if knob in ('left', 'both'):
        c.circle(x + h / 2, y + h / 2, r, LIGHT if d >= 1 else FG)
    tx = x + (h if knob in ('left', 'both') else 18)
    c.label(tx, y + h / 2, t, 14, 500, ink=DARK if solid else INK, bar=FG2 if solid else FG, maxw=w - 36)


def p_opill(c, n, x, y, w, h, d, tone):
    c.rect(x + .5, y + .5, w - 1, h - 1, h / 2, 'none', LIGHT, 1)
    c.label(x + w / 2, y + h / 2, n.args[0] if n.args else '', 11, 500, anchor='middle', maxw=w - 16)


def p_button(c, n, x, y, w, h, d, tone):
    ghost = 'ghost' in n.opts
    c.rect(x + (.5 if ghost else 0), y, w, h, h / 2, 'none' if ghost else LIGHT, LIGHT if ghost else None)
    c.label(x + w / 2, y + h / 2, n.args[0] if n.args else 'Botão', 14, 600, ink=INK if ghost else DARK, bar=FG if ghost else FG2, anchor='middle', maxw=w - 20)


def p_dot(c, n, x, y, w, h, d, tone):
    s = min(w, h); c.circle(x + w / 2, y + h / 2, s / 2, TONES[1] if d == 0 else FG)   # on the panel itself, a dot is a quiet button


def p_dots(c, n, x, y, w, h, d, tone):
    s = n.num('size', 36)
    for i in range(int(n.num('n', 5))):
        c.circle(x + s / 2 + i * (s + 6), y + h / 2, s / 2, FG)


def p_avatars(c, n, x, y, w, h, d, tone):
    s = n.num('size', 36)
    for i in range(int(n.num('n', 5))):
        c.circle(x + s / 2 + i * s * 0.68, y + h / 2, s / 2, FG, tone, 2)


def p_divider(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, 1, 0, FG2)


def p_progress(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, h, h / 2, tone); c.rect(x, y, w * n.num('pct', 60) / 100, h, h / 2, LIGHT)


def p_toggle(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, h, h / 2, tone); c.circle(x + w - h / 2, y + h / 2, h / 2 - 3, LIGHT)


def p_input(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, h, 12, tone)
    c.label(x + 16, y + h / 2, n.args[0] if n.args else 'Digite aqui', 14, ink=INK2, bar=FG2, maxw=w - 60)
    if kind_is_select(n):
        c.path(f'M{x + w - 28} {y + h / 2 - 3}l6 6 6-6', stroke=FG, sw=2)


def kind_is_select(n):
    return n.kind == 'select'


def p_kpi(c, n, x, y, w, h, d, tone):
    num = n.args[0] if n.args else 'R$ 90.235'; rot = n.args[1] if len(n.args) > 1 else 'indicador'
    size = n.num('size', 30); top = y + (h - size * 1.2 - 20 - (18 if 'delta' in n.opts else 0)) / 2
    c.label(x, top + size * .6, num, size, 600, bar=LIGHT, maxw=w)
    c.label(x, top + size * 1.2 + 11, rot, 13, ink=INK2, bar=FG2, maxw=w)
    if 'delta' in n.opts:
        c.label(x, top + size * 1.2 + 30, n.opts['delta'], 12, 500, ink=INK2, bar=FG2, maxw=w)


def p_bars(c, n, x, y, w, h, d, tone):
    vals = [float(v) for v in n.opts['values'].split(',')] if 'values' in n.opts else [.35 + .55 * abs(math.sin(i * 1.3 + 1)) * (.5 + i / 24) for i in range(int(n.num('n', 12)))]
    top = max(vals); k = len(vals); bw = w / k * .62
    labels = n.items('labels'); lh = 20 if labels else 0
    for i, v in enumerate(vals):
        bh = (h - lh) * v / top
        c.rect(x + i * w / k + (w / k - bw) / 2, y + h - lh - bh, bw, bh, min(8, bw / 2), LIGHT if i == k - 1 else FG)
        if i < len(labels):
            c.label(x + i * w / k + w / k / 2, y + h - 8, labels[i], 11, ink=INK2, bar=FG2, anchor='middle')


def curve(n, x, y, w, h):
    vals = [float(v) for v in n.opts['values'].split(',')] if 'values' in n.opts else [.3, .42, .38, .55, .5, .68, .62, .78, .72, .9]
    top = max(vals)
    return [(x + i * w / (len(vals) - 1), y + h - h * v / top * .92) for i, v in enumerate(vals)]


def p_line(c, n, x, y, w, h, d, tone):
    pts = curve(n, x, y, w, h)
    c.path('M' + ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts), stroke=LIGHT, sw=3)


def p_area(c, n, x, y, w, h, d, tone):
    pts = curve(n, x, y, w, h)
    line = ' L'.join(f'{a:.1f} {b:.1f}' for a, b in pts)
    c.path(f'M{line} L{x + w:.1f} {y + h:.1f} L{x:.1f} {y + h:.1f} Z', fill=FG2, op=.55)
    c.path('M' + line, stroke=LIGHT, sw=3)


p_spark = p_line


def p_donut(c, n, x, y, w, h, d, tone):
    r = min(w, h) / 2 - 12; cx, cy = x + w / 2, y + h / 2; pct = n.num('pct', 54)
    c.circle(cx, cy, r, 'none', tone, 18)
    a = 2 * math.pi * pct / 100 - math.pi / 2
    c.path(f'M{cx:.1f} {cy - r:.1f} A{r:.1f} {r:.1f} 0 {1 if pct > 50 else 0} 1 {cx + r * math.cos(a):.1f} {cy + r * math.sin(a):.1f}', stroke=LIGHT, sw=18)
    c.label(cx, cy, n.args[0] if n.args else f'{pct:.0f}%', max(16, r * .42), 600, anchor='middle', bar=LIGHT)


def p_funnel(c, n, x, y, w, h, d, tone):
    labels = n.items('labels') or ['', '', '', ''][:int(n.num('n', 4))]
    k = len(labels); gap = 8; bh = (h - gap * (k - 1)) / k
    for i, t in enumerate(labels):
        bw = w * (1 - i * .62 / max(1, k - 1)); by = y + i * (bh + gap)
        c.rect(x, by, bw, bh, 10, FG if i else LIGHT)
        c.label(x + 14, by + bh / 2, t, 13, 500, ink=DARK if not i else INK, bar=FG2, maxw=bw - 24)


def p_table(c, n, x, y, w, h, d, tone):
    cols = n.items('cols') or ['', '', '', '']; rows = int(n.num('rows', 6)); rh = h / (rows + 1)
    cw = w / len(cols)
    for j, t in enumerate(cols):
        c.label(x + j * cw + 8, y + rh / 2, t or 'Coluna', 12, 600, ink=INK2, bar=FG2, maxw=cw - 16)
    data = [r.split(',') for r in n.items('data')]
    for i in range(rows):
        ry = y + (i + 1) * rh
        c.rect(x, ry, w, 1, 0, TONES[min(d + 2, 4)])
        for j in range(len(cols)):
            if i < len(data) and j < len(data[i]):
                c.label(x + j * cw + 8, ry + rh / 2, data[i][j], 13, maxw=cw - 16)
            else:
                c.rect(x + j * cw + 8, ry + rh / 2 - 5, (cw - 24) * [.8, .55, .68, .45][(i + j) % 4], 10, 5, FG)


def p_list(c, n, x, y, w, h, d, tone):
    items = n.items() or [''] * int(n.num('n', 4)); rh = h / len(items)
    for i, t in enumerate(items):
        cy = y + i * rh + rh / 2; c.circle(x + 15, cy, 15, FG)
        if t:
            c.label(x + 42, cy, t, 14, maxw=w - 42)
        else:
            c.rect(x + 42, cy - 12, (w - 42) * .7, 10, 5, FG); c.rect(x + 42, cy + 4, (w - 42) * .45, 8, 4, FG2)


def p_calendar(c, n, x, y, w, h, d, tone):
    cw, rh = w / 7, h / 6
    for i, l in enumerate('DSTQQSS'):
        c.label(x + (i + .5) * cw, y + rh / 2, l, 11, 600, ink=INK2, bar=FG2, anchor='middle')
    today = n.num('today', 17)
    for i in range(30):
        cx, cy = x + (i % 7 + .5) * cw, y + (i // 7 + 1.5) * rh
        if i + 1 == today:
            c.circle(cx, cy, min(cw, rh) * .4, LIGHT)
        c.label(cx, cy, str(i + 1), 12, ink=DARK if i + 1 == today else INK, bar=FG2 if i + 1 == today else FG, anchor='middle')


def p_kanban(c, n, x, y, w, h, d, tone):
    cols = n.items('cols') or ['', '', '', '']; cards = int(n.num('cards', 3)); g = 12; cw = (w - g * (len(cols) - 1)) / len(cols)
    for j, t in enumerate(cols):
        cx = x + j * (cw + g); c.rect(cx, y, cw, h, 16, tone)
        c.label(cx + 14, y + 22, t or 'Etapa', 13, 600, maxw=cw - 28)
        ch = (h - 44 - 10 * cards) / cards
        for i in range(cards):
            cy = y + 44 + i * (ch + 10); c.rect(cx + 8, cy, cw - 16, ch, 12, TONES[min(d + 2, 4)])
            c.rect(cx + 20, cy + 14, (cw - 40) * .75, 10, 5, FG); c.rect(cx + 20, cy + 32, (cw - 40) * .5, 8, 4, FG2)


def p_navbar(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, h, h / 2, tone)
    c.label(x + 26, y + h / 2, n.args[0] if n.args else 'Marca', 17, 600, bar=LIGHT)
    links = n.items('links') or ['Produto', 'Preços', 'Sobre', 'Blog']
    cta = n.opts.get('cta', 'Começar'); bw = max(110, chars(cta, 14) + 36)
    lx = x + w - bw - 40 - sum(chars(t, 14) + 28 for t in links)
    for t in links:
        c.label(lx, y + h / 2, t, 14, ink=INK2, bar=FG); lx += chars(t, 14) + 28
    c.rect(x + w - bw - 10, y + 10, bw, h - 20, (h - 20) / 2, LIGHT)
    c.label(x + w - bw / 2 - 10, y + h / 2, cta, 14, 600, ink=DARK, bar=FG2, anchor='middle')


def p_tabs(c, n, x, y, w, h, d, tone):
    tabs = n.items() or [''] * int(n.num('n', 5)); act = int(n.num('active', 1)) - 1; g = 8
    tw = (w - g * (len(tabs) - 1)) / len(tabs)
    for i, t in enumerate(tabs):
        tx = x + i * (tw + g); on = i == act
        c.rect(tx, y, tw, h, h / 2, LIGHT if on else tone)
        c.label(tx + tw / 2, y + h / 2, t or 'Aba', 13, 500, ink=DARK if on else INK, bar=FG2 if on else FG, anchor='middle', maxw=tw - 16)


def p_sidebar(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, h, 22, tone)
    items = n.items(); k = len(items) or int(n.num('n', 8)); rh = min(52, (h - 24) / k)
    for i in range(k):
        cy = y + 12 + (i + .5) * rh
        c.circle(x + 28, cy, 10, LIGHT if i == 0 else FG)
        if items and w > 90:
            c.label(x + 50, cy, items[i], 14, 500 if i == 0 else 400, ink=INK if i == 0 else INK2, maxw=w - 60)


def p_hero(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, h, 26, tone)
    tw = w * .46; size = n.num('size', 46); t = n.args[0] if n.args else 'Título principal da página em duas linhas'
    rows = wrap(t, size, tw); lh = size * 1.15; sub = n.args[1] if len(n.args) > 1 else 'Uma frase de apoio explicando o que o produto faz e para quem.'
    srows = wrap(sub, 17, tw); total = lh * len(rows) + 18 + 25 * len(srows) + 26 + 50
    ty = y + (h - total) / 2
    for i, r in enumerate(rows):
        c.label(x + 44, ty + lh * (i + .5), r, size, 600, bar=LIGHT, maxw=tw)
    sy = ty + lh * len(rows) + 18
    for i, r in enumerate(srows):
        c.label(x + 44, sy + 25 * (i + .5), r, 17, ink=INK2, bar=FG, maxw=tw)
    cta = n.opts.get('cta', 'Começar agora'); by = sy + 25 * len(srows) + 26; bw = chars(cta, 15) + 48
    c.rect(x + 44, by, bw, 50, 25, LIGHT); c.label(x + 44 + bw / 2, by + 25, cta, 15, 600, ink=DARK, bar=FG2, anchor='middle')
    c.rect(x + w * .54, y + 28, w * .46 - 28, h - 56, 20, TONES[min(d + 2, 4)])


def p_cardgrid(c, n, x, y, w, h, d, tone):
    k, cols = int(n.num('n', 6)), int(n.num('cols', 3)); g = 16; rows = math.ceil(k / cols)
    names = n.items(); cw, ch = (w - g * (cols - 1)) / cols, (h - g * (rows - 1)) / rows
    for i in range(k):
        cx, cy = x + i % cols * (cw + g), y + i // cols * (ch + g)
        c.rect(cx, cy, cw, ch, 20, tone); c.rect(cx + 12, cy + 12, cw - 24, ch * .55, 12, TONES[min(d + 2, 4)])
        ty = cy + 12 + ch * .55 + 22
        if i < len(names):
            c.label(cx + 16, ty, names[i], 16, 600, maxw=cw - 32)
        else:
            c.rect(cx + 16, ty - 7, (cw - 32) * .7, 14, 7, FG)
        c.rect(cx + 16, ty + 18, (cw - 32) * .5, 9, 4, FG2)


def p_footer(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, h, 22, tone); cols = int(n.num('cols', 4)); cw = (w - 48) / cols
    for j in range(cols):
        fx = x + 24 + j * cw; c.rect(fx, y + 26, cw * .4, 12, 6, LIGHT)
        for i in range(3):
            c.rect(fx, y + 54 + i * 24, cw * [.55, .42, .5][i], 9, 4, FG)


def p_tabbar(c, n, x, y, w, h, d, tone):
    c.rect(x, y, w, h, h / 2, tone); k = int(n.num('n', 5)); act = int(n.num('active', 1)) - 1
    for i in range(k):
        c.circle(x + (i + .5) * w / k, y + h / 2, 12, LIGHT if i == act else FG)


def p_fan(c, n, x, y, w, h, d, tone):
    # a fanned stack of cards, cut off by the bottom edge of the piece
    k = int(n.num('n', 4)); cid = f'f{int(x)}{int(y)}'
    c.out.append(f'<clipPath id="{cid}"><rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}"/></clipPath><g clip-path="url(#{cid})">')
    cw = w * .5
    for i in range(k):
        cx, cy = x + w * .34 + i * w * .13, y + h * .5 - i * h * .13
        c.out.append(f'<g transform="rotate({-34 + i * 11} {cx + cw / 2:.1f} {cy + h:.1f})">')
        c.rect(cx, cy, cw, h * 1.3, 16, ['#6e6e6e', '#7e7e7e', '#969696', LIGHT][min(i, 3)])
        c.out.append('</g>')
    c.out.append('</g>')


PIECES = {'card': p_card, 'image': p_image, 'title': p_title, 'text': p_text, 'lines': p_lines, 'pill': p_pill, 'opill': p_opill, 'button': p_button, 'dot': p_dot, 'dots': p_dots,
          'avatars': p_avatars, 'divider': p_divider, 'progress': p_progress, 'toggle': p_toggle, 'input': p_input, 'select': p_input, 'kpi': p_kpi, 'bars': p_bars, 'line': p_line,
          'area': p_area, 'spark': p_spark, 'donut': p_donut, 'funnel': p_funnel, 'table': p_table, 'list': p_list, 'calendar': p_calendar, 'kanban': p_kanban, 'navbar': p_navbar,
          'tabs': p_tabs, 'sidebar': p_sidebar, 'hero': p_hero, 'cardgrid': p_cardgrid, 'footer': p_footer, 'tabbar': p_tabbar, 'fan': p_fan}


def render(path, text_mode, font):
    (name, opts), root = parse(path)
    m = re.fullmatch(r'(\d+)x(\d+)', name)
    W, H, M = (int(m[1]), int(m[2]), 56) if m else SCREENS.get(name) or SCREENS['dashboard']
    M = int(opts.get('margin', M))
    root.opts.setdefault('pad', '20')
    if root.kind in PLAIN:
        root.opts.setdefault('gap', '12')
    if not H:                       # site: the height grows with the content
        H = int(nat_h(root) + 2 * M)
    layout(root, M, M, W - 2 * M, H - 2 * M)
    c = Canvas(text_mode, font)
    c.rect(M, M, W - 2 * M, H - 2 * M, 28, TONES[0])
    for k in ([root] if root.kind not in PLAIN else []):
        draw(c, k, 0)
    if root.kind in PLAIN:
        for k in root.kids:
            draw(c, k, 0)
    family = f' font-family="{html.escape(font)}, sans-serif"' if text_mode else ''
    grain = (f'<filter id="g"><feTurbulence type="fractalNoise" baseFrequency=".9" numOctaves="2" stitchTiles="stitch"/><feColorMatrix values="0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 0 {GRAIN * 2} 0"/></filter>'
             f'<rect width="100%" height="100%" fill="{PAGE}"/><rect width="100%" height="100%" filter="url(#g)"/>')
    return W, H, f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {W} {H}" width="{W}" height="{H}"{family}>{grain}{"".join(c.out)}</svg>'


# ---------- output ----------
def shoot(jobs):
    """jobs: (file to open, png path, width, height)."""
    from playwright.sync_api import sync_playwright
    with sync_playwright() as p:
        b = p.chromium.launch(channel='chrome')
        for src, png, w, h in jobs:
            pg = b.new_page(viewport={'width': int(w), 'height': int(h)})
            if str(src).endswith('.svg'):          # a bare SVG document cannot be screenshotted: wrap it
                pg.set_content('<!doctype html><style>html,body{margin:0}svg{display:block}</style>' + Path(src).read_text(encoding='utf-8'))
            else:
                pg.goto(Path(src).resolve().as_uri())
            pg.evaluate('document.fonts ? document.fonts.ready : null')
            pg.wait_for_timeout(250)
            pg.screenshot(path=str(png), full_page=True)
            pg.close()
        b.close()


def side_by_side(paths, out, labels=None, height=520):
    cells = ''.join(f'<figure><img src="{Path(q).resolve().as_uri()}"><figcaption>{html.escape(labels[i] if labels else Path(q).stem)}</figcaption></figure>' for i, q in enumerate(paths))
    page = Path(out).with_suffix('.html')
    page.write_text(f'<!doctype html><meta charset="utf-8"><style>body{{margin:0;padding:20px;background:#e9e9e9;display:flex;flex-wrap:wrap;gap:20px;font:13px system-ui;color:#333;width:fit-content;max-width:2400px}}figure{{margin:0}}img{{height:{height}px;display:block;border-radius:6px}}figcaption{{padding-top:8px}}</style>{cells}', encoding='utf-8')
    return page


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('layouts', nargs='+')
    ap.add_argument('--out', default='.')
    ap.add_argument('--text', action='store_true', help='real text (HTML + PNG) instead of bars (SVG + PNG)')
    ap.add_argument('--font', default='Inter', help='Google Font, or several separated by commas')
    ap.add_argument('--compare', help='reference image: also writes <name>-compare.png')
    a = ap.parse_args()
    out = Path(a.out); out.mkdir(parents=True, exist_ok=True)
    jobs, pngs = [], []
    fonts = [f.strip() for f in a.font.split(',')] if a.text else [None]
    for lay in a.layouts:
        for font in fonts:
            stem = Path(lay).stem
            if a.text:
                W, H, svg = render(lay, True, font)
                slug = re.sub(r'[^a-z0-9]+', '-', font.lower())
                src = out / f'{stem}-text-{slug}.html'
                link = font.replace(' ', '+')
                src.write_text(f'<!doctype html><html><head><meta charset="utf-8"><title>{html.escape(stem)}</title><link rel="stylesheet" href="https://fonts.googleapis.com/css2?family={link}:wght@300;400;500;600;700&display=swap"><style>html,body{{margin:0}}svg{{display:block}}</style></head><body>{svg}</body></html>', encoding='utf-8')
            else:
                W, H, svg = render(lay, False, None)
                src = out / f'{stem}.svg'
                src.write_text(svg, encoding='utf-8')
            png = src.with_suffix('.png')
            jobs.append((src, png, W, H)); pngs.append(png)
    shoot(jobs)
    extra = []
    if len(pngs) > 1:
        page = side_by_side(pngs, out / 'sheet.png')
        extra.append((page, out / 'sheet.png', 1600, 700))
    if a.compare:
        page = side_by_side([a.compare, pngs[0]], out / f'{Path(a.layouts[0]).stem}-compare.png', ['reference', 'wireframe'], 620)
        extra.append((page, out / f'{Path(a.layouts[0]).stem}-compare.png', 1600, 700))
    if extra:
        shoot(extra)
        for page, *_ in extra:
            Path(page).unlink()
    for p in pngs + [e[1] for e in extra]:
        print(p)


if __name__ == '__main__':
    main()
