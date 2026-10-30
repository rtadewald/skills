#!/usr/bin/env python3
"""Cheap structural validation for the Animate catalog."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / 'assets/js/catalog.js'
ANIMATIONS = ROOT / 'assets/animations'


def main() -> int:
    errors: list[str] = []
    required = [
        ROOT / 'SKILL.md',
        ROOT / 'SPECS.md',
        ROOT / 'index.html',
        ROOT / 'agents/openai.yaml',
        REGISTRY,
    ]
    for path in required:
        if not path.is_file():
            errors.append(f'missing: {path.relative_to(ROOT)}')

    source = REGISTRY.read_text() if REGISTRY.is_file() else ''
    ids = re.findall(r"id: '((?:CMP|IDL|INT|BG)-\d{2})'", source)
    if len(ids) != len(set(ids)):
        errors.append('duplicate animation IDs in catalog.js')
    modes = re.findall(r"mode: '([^']+)'", source)
    if len(modes) != len(ids):
        errors.append('every registered item must declare a mode')
    invalid_modes = sorted(set(modes) - {'components', 'backgrounds'})
    if invalid_modes:
        errors.append(f'invalid catalog modes: {", ".join(invalid_modes)}')
    if 'components:' not in source or 'backgrounds:' not in source:
        errors.append('catalog must define components and backgrounds modes')
    if re.search(r"(?:TRN-\d{2}|mode: '(?:idle|transitions|interactions)')", source):
        errors.append('retired animation modes or TRN IDs remain in catalog.js')

    folders = re.findall(r"folder: `\$\{item\.id\.toLowerCase\(\)\}-\$\{item\.slug\}`", source)
    if not folders:
        errors.append('catalog path derivation missing')

    for directory in sorted(ANIMATIONS.iterdir()) if ANIMATIONS.is_dir() else []:
        if not directory.is_dir():
            continue
        for name in ('meta.json', 'demo.html', 'styles.css', 'script.js'):
            if not (directory / name).is_file():
                errors.append(f'{directory.name}: missing {name}')
        meta_path = directory / 'meta.json'
        if meta_path.is_file():
            try:
                meta = json.loads(meta_path.read_text())
                if meta.get('id', '').lower() not in directory.name:
                    errors.append(f'{directory.name}: metadata ID does not match folder')
                mode = meta.get('mode')
                if mode not in {'components', 'backgrounds'}:
                    errors.append(f'{directory.name}: invalid metadata mode {mode!r}')
                identifier = meta.get('id', '')
                if mode == 'backgrounds' and not identifier.startswith('BG-'):
                    errors.append(f'{directory.name}: backgrounds must use BG- IDs')
                if mode == 'components' and not identifier.startswith(('CMP-', 'IDL-', 'INT-')):
                    errors.append(f'{directory.name}: invalid component ID prefix')
            except json.JSONDecodeError as exc:
                errors.append(f'{directory.name}: invalid meta.json ({exc})')

    package_count = sum(1 for path in ANIMATIONS.iterdir() if path.is_dir()) if ANIMATIONS.is_dir() else 0
    if package_count != len(ids):
        errors.append(f'expected {len(ids)} packages, found {package_count}')

    if errors:
        print('Animate validation failed:')
        for error in errors:
            print(f'- {error}')
        return 1
    print(f'Animate validation passed: {len(ids)} IDs, {package_count} packages.')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
