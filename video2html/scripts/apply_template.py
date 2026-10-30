# /// script
# requires-python = ">=3.11"
# ///
"""Update a character page made from templates/character.html to the latest template, keeping the page's settings.

    uv run apply_template.py <page.html> [--template ../templates/character.html]

The SETTINGS block of the page (from "// ---------- SETTINGS" to the first blank line) is kept as is; settings that the
template has and the page does not are added with the template's default. Everything else comes from the template.
The page's <html lang> is kept.
"""
from __future__ import annotations

import argparse
import re
from pathlib import Path

HEAD = '// ---------- SETTINGS'


def block(text: str) -> tuple[int, int]:
    a = text.index(HEAD)
    return a, text.index('\n\n', a)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument('page')
    ap.add_argument('--template', default=str(Path(__file__).resolve().parent.parent / 'templates' / 'character.html'))
    a = ap.parse_args()
    page, tpl = Path(a.page).read_text(encoding='utf-8'), Path(a.template).read_text(encoding='utf-8')
    pa, pb = block(page)
    ta, tb = block(tpl)
    mine = page[pa:pb]
    names = set(re.findall(r'^const (\w+) =', mine, re.M))
    added = [l for l in re.findall(r'^const \w+ = .*$', tpl[ta:tb], re.M) if re.match(r'const (\w+)', l).group(1) not in names]
    out = tpl[:ta] + mine + ('\n' + '\n'.join(added) if added else '') + tpl[tb:]
    lang = re.search(r'<html lang="([^"]+)"', page)
    if lang:
        out = re.sub(r'<html lang="[^"]+"', f'<html lang="{lang.group(1)}"', out, count=1)
    Path(a.page).write_text(out, encoding='utf-8')
    print(f'{a.page}: updated; new settings: {", ".join(re.match(r"const (\w+)", l).group(1) for l in added) or "none"}')


if __name__ == '__main__':
    main()
