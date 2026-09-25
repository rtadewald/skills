---
name: extract-ds3
description: >-
  Quickly turn a finished local HTML page or website into a copy-first design
  system catalog. Deliver a minimally adapted Overview first; extract Components
  only after approval.
---

# Extract DS 3

Build a design system catalog from a finished local page. The first handoff must
be fast: copy the working project, make small safe edits, wrap it as Overview,
and show it to the user.

The catalog has exactly two views:

1. **Overview** — a working copy of the page with its main visible copy adapted
   to describe the observed design system.
2. **Components** — live foundations and components extracted only after the
   user approves Overview.

Do not redesign, rebuild, optimize, audit, or reverse-engineer the source.

## Speed contract

For an ordinary local page, target the Overview handoff in about 1–2 minutes.
Favor a useful working copy over a minimal or exhaustively verified package.

- Copy first; inspect only what blocks copying or opening.
- Prefer one broad copy over tracing every dependency.
- Make direct edits; do not create transformation or comparison scripts.
- Do not analyze or rewrite minified/generated bundles.
- Do not run visual diffs, geometry comparisons, exhaustive audits, or broad
  interaction tests.
- Do not start two servers or try multiple browser stacks.
- Do not open a browser during the normal Overview path. Use one brief smoke
  test only when the copy is visibly or evidently broken, or when requested.
- Stop as soon as Overview is usable and the catalog opens.

## Input, output, and phases

`$SOURCE` is a finished HTML file or local website. Treat it as read-only.

`$OUTPUT` defaults to `<source-name>-design-system/` beside the source. Create
new files only inside it. The entry point is `$OUTPUT/design-system.html`, and
Overview normally lives at `$OUTPUT/assets/overview/index.html`.

- No approved Overview: build only Overview and stop.
- Overview correction: change only Overview/catalog shell and stop.
- Approved Overview: build Components.
- Existing output: continue from its latest approved phase.

## Fast runtime decision

Decide from one shallow pass over the entry page and obvious scripts:

- Use `file://` when relative HTML, CSS, images, fonts, and classic scripts can
  work directly, including after small path or packaging changes.
- Use a minimal local server when modules, fetch/CORS, routing, workers, or a
  runtime loader make `file://` unreliable.
- Do not test both approaches. Do not debug a complex runtime merely to force
  `file://`; state the server requirement and continue.
- Keep working CDN references. Offline packaging is out of scope unless asked.

## Phase 1 — Fast Overview

### 1. Copy

Locate the active entry page, normally `index.html`. Copy its containing project
or the smallest obvious working subtree into `$OUTPUT/assets/overview/`, keeping
relative paths intact.

It is acceptable to copy some unused local assets when that is faster and safer
than tracing references. Exclude only obvious bulk or unrelated material such as
`node_modules`, caches, source maps, tests, drafts, screenshots, and editor files.

Do not inventory the whole project or follow every CSS/JavaScript import.

### 2. Adapt the copy minimally

Work only in the copy.

- Rewrite prominent visible copy: hero, section headings, short descriptions,
  and relevant CTA labels. Describe only visual qualities present in the page.
- Preserve text slots, hierarchy, spans, effects, approximate lengths, markup,
  classes, styles, assets, and interactions.
- Remove comments, analytics, tracking, and production integrations only when
  the edit is obvious and safe. Do not perform a cleanup audit.
- For static HTML, replace text directly.
- For generated pages whose text lives in bundles, do not edit the bundle.
  Inject a short end-of-body DOM text map when necessary and move on.
- Leave legal or incidental interface copy unchanged when adapting it would
  require runtime surgery.

Do not recreate components, reorganize CSS, rename runtime files, extract inline
code, minify, replace libraries, optimize media, or audit unused selectors.

### 3. Wrap it in the catalog

Create `$OUTPUT/design-system.html` with:

```text
Overview | Components
```

If the source has a navbar, adapt it into the catalog navbar: reuse its identity,
logo, size, styling, and responsive behavior; replace destinations with Overview
and Components; suppress the duplicate navbar and spacer inside Overview. Never
stack a generic navbar above the source navbar.

Use `#overview` and `#components`, select Overview initially, and keep Components
disabled until approval. Display Overview in a borderless iframe filling the area
below the navbar. Do not add documentation, cards, device frames, or browser chrome.

### 4. Hand off immediately

Perform only a cheap structural check: entry files exist, iframe/path targets are
correct, and the chosen runtime command is clear. Do not validate original and
copy side by side as a routine step.

Deliver the exact `design-system.html` path, say whether it opens via `file://` or
give one minimal server command, and ask for Overview approval. Stop.

## Phase 2 — Components after approval

Inspect the approved Overview from beginning to end. Document only elements and
states visible there or reachable through a real interaction. Ignore unused code
and unobserved variants.

Read [references/component-formats.md](references/component-formats.md) only now,
and only the sections relevant to observed groups. Put foundations first, then
complete components. Omit empty groups and do not create a separate inventory.

Enable Components in the existing catalog. Add a sticky left sidebar containing
only group names and stack all groups in the main area. Reuse Overview HTML, CSS,
copy, assets, states, effects, and required context. Group repeated instances and
store source selectors as code metadata instead of verbose visible provenance.

Smoke-test only the catalog switching, hashes, scrolling, and the representative
states actually documented. Investigate deeper only when something is visibly
broken or the user requests it. Deliver the same catalog and ask for approval.
