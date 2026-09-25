---
name: extract-ds
description: >-
  Build a design system from a finished local website by copying its repository,
  rapidly identifying whether it runs through file:// or a local server, and
  preserving its main animations. Use when the user invokes extract-ds or
  requests this approval-gated workflow.
---

# Extract DS

You are a Design System Builder.

The user will give you a finished local website. Copy its repository into a new
design system and preserve its structure, visual identity, interactions, main
animations, and chosen runtime.

Work in two approval-gated phases: first deliver Overview and stop; only after the
user approves it, build Components and stop for approval again. Do not redesign
or rebuild the source.

## Required outcome

- Copy the source project into the new design system output.
- Rapidly determine whether the source currently runs through `file://` or a
  local server.
- When it requires a server, ask whether the user wants the slower `file://`
  conversion or the faster server-preserving path.
- Preserve the page structure, styling, effects, interactions, and main animations.
- Adapt the hero copy to present `<observed brand> Design System`.
- Replace the remaining visible page copy with generic Lorem Ipsum.
- Present Overview and stop for explicit approval.
- Build Components only after that approval, then present it and stop for a
  second explicit approval.

## Output naming

Unless the user provides an explicit destination, create `$OUTPUT` beside
`$SOURCE` with the exact pattern:

```text
<brand-name>-design-system/
```

Derive `<brand-name>` from the brand visibly presented by the source, not from
the repository folder, domain, page title suffix, campaign, or technical project
name. Normalize it to lowercase kebab-case. Reuse that same folder during
Overview corrections and the Components phase; do not create numbered copies.

The catalog entry point is `$OUTPUT/design-system.html`.

## Runtime preflight

Before creating `$OUTPUT`, make one shallow inspection of the source runtime.
Check only the entry page, obvious project instructions or start scripts, and
clear runtime signals such as local ES modules, fetch/XHR, routing, workers,
WASM, or root-relative assets. Do not start a server, open a browser, trace every
dependency, or prove both modes.

Classify the source as one of these:

- **Runs through `file://`** — continue directly to Phase 1 without asking.
- **Requires a local server** — briefly name the reason and ask the user:
  “Este projeto roda atualmente por servidor local. Quer que eu o adapte para
  `file://`? Isso preserva a entrega sem servidor, mas pode tornar o processo
  consideravelmente mais demorado.”

If the user says yes, set the chosen runtime to `file://` and begin Overview by
performing that conversion. If the user says no, preserve the existing server
runtime and prioritize delivery speed. Stop and wait for the answer before
creating Overview. Do not ask when the user already stated a runtime preference.

## Working principles

- Copy first; inspect only what is needed to preserve runtime behavior.
- Prefer direct, local changes over rebuilding the project.
- Keep existing filenames, directories, markup, classes, CSS, and assets.
- Do not audit unused code, optimize media, reorganize styles, or reverse-engineer
  minified bundles.
- Do not create analysis, transformation, or comparison scripts for one-off work.
- Do not compare original and copy pixel by pixel or start multiple servers.
- Keep working CDN resources unless offline packaging was explicitly requested.

## Phase 1 — Overview

### 1. Copy the project

Treat `$SOURCE` as read-only. Copy the repository or complete working project into:

```text
$OUTPUT/assets/overview/
```

Preserve its internal paths and include the files needed by its runtime. Exclude
only repository metadata and obvious development bulk that the finished page does
not load, such as `.git`, caches, source maps, test output, and `node_modules`.
It is better to include a few unused assets than to spend time tracing every
dependency.

Locate the copied entry page, normally `assets/overview/index.html`. Make all
subsequent changes only inside `$OUTPUT`.

### 2. Preserve or adapt the chosen runtime

If the source already runs through `file://`, preserve that behavior and make
only necessary path fixes.

If the user chose the fast server path, retain the existing start command and
runtime structure. Do not convert modules, fetches, routing, workers, or binary
loaders merely to remove the server.

If the user approved conversion from a server to `file://`, preserve the main
animations while adapting only the mechanisms that require an HTTP origin.

Use the smallest relevant fixes:

- keep relative HTML, CSS, image, media, and classic-script paths;
- rewrite root-relative paths to paths relative to the copied entry page;
- bundle local ES module graphs into browser-ready classic scripts when needed;
- keep remote CDN scripts and fonts when they work from a `null` origin;
- replace blocked local font loading with permitted CDN loading or embedded data;
- adapt local `fetch`/XHR binary loading for images, JSON, WASM, Rive, GLB, HDR,
  and similar assets with local maps, embedded data, Blob URLs, or equivalent;
- adapt Workers and WASM initialization only when used by a main animation;
- keep navigation inside the copied Overview instead of relying on server routes;
- avoid parent/iframe origin access from the Overview.

Preserve the source's main visual motion, especially hero/background WebGL, canvas,
Rive, marquee, scroll, and entrance animations. Production APIs, analytics,
tracking, authentication, checkout, and secondary routes do not need emulation.

During an approved `file://` conversion, do not silently fall back to a server.
If a protected remote service, DRM, or another external restriction makes a main
animation genuinely impossible through `file://`, report the exact blocker and
ask whether to continue with the existing server runtime.

### 3. Replace the copy

In the hero:

- use the observed brand or product name followed by `Design System`;
- use a short supporting sentence describing only visible visual qualities;
- keep the existing hierarchy, spans, line breaks, effects, and approximate length.

Everywhere else, replace visible marketing/editorial copy with generic Lorem Ipsum
of roughly similar length. Preserve element structure so layout and animation hooks
continue to work. Keep functional or accessibility text only when changing it
would break behavior.

For static HTML, edit text directly. If text is generated by a bundle, do not edit
the minified bundle: use a small early DOM text mapping in the copied page, timed
before animation initialization when necessary.

Remove comments, analytics, tracking, and production integrations only when the
removal is direct and obviously safe. Do not perform a cleanup audit.

### 4. Create the catalog and navbar

Create `$OUTPUT/design-system.html` with:

```text
Overview | Components
```

If the source already has a navbar, adapt it into the catalog navbar. Reuse its
identity, logo, dimensions, styling, and responsive behavior; replace its
destinations with Overview and Components; suppress the duplicate navbar and its
spacer inside Overview. Never stack a generic catalog navbar above the original.

If no navbar exists, derive a minimal one from the source's visual language.

Use `#overview` and `#components`, preserve browser history, and select Overview
initially. Show Components as disabled until approval. Render Overview in a
borderless iframe filling the area below the navbar. Do not add cards, device
frames, browser chrome, or documentation around it.

### 5. Check and present Overview

Perform one short check using the chosen runtime. For `file://`, open the exact
catalog file. For the server path, reuse the existing minimal start command and
do not introduce another server. Confirm:

- Overview loads through the chosen runtime;
- the main animations initialize;
- the adapted navbar is the only top navbar;
- no missing local file prevents the page from rendering.

Fix only concrete blockers found in this check. Do not compare against the
original, create comparison tooling, or expand into a general audit.

Deliver the exact `design-system.html` path, state whether it opens through
`file://` or give the existing minimal server command, show Overview to the user,
and request explicit approval. Stop.

## Phase 2 — Components after Overview approval

After approval, inspect only the approved Overview. A foundation, component,
variant, or state may be documented only when visible there or reachable through
a real interaction.

Read [references/component-formats.md](references/component-formats.md) now and
follow only the sections relevant to observed groups. Put foundations first, then
complete components. Omit empty groups and group repeated instances.

Enable Components in the existing catalog. Add a sticky left sidebar containing
only group names and stack all groups in the main area. Every specimen must reuse
Overview HTML, CSS, Lorem Ipsum copy, assets, states, effects, and required context.
Store selectors or sources as code metadata instead of verbose visible provenance.

Keep the completed catalog compatible with the runtime chosen before Overview.
Perform one short smoke test of Overview/Components switching, hashes, scrolling,
and representative documented states. Fix concrete failures only.

Present Components to the user and request explicit approval again. Stop.
