---
name: ds-from-react
description: >-
  Host a React application, inspect its running UI and source files, then create one
  design-system.html living pattern library using only its existing styles, assets,
  components, and motion. Use when the user asks for a design system from a React app.
disable-model-invocation: true
---

# React app → Design system HTML

You are given a React application directory:

`$ARGUMENTS`

Create one new file, `design-system.html`, that documents the application's real design system as a living pattern library. The file must be faithful to the application, not a redesign or an approximation.

## Outcome

- Host the supplied React application before extracting anything.
- Inspect both the running application and its source files.
- Create only `design-system.html` as the new deliverable, in the application root unless the user specifies another location.
- Keep the app's existing source, configuration, dependencies, and build setup unchanged.

`design-system.html` may reference the application's existing compiled CSS, fonts, images, icons, and scripts. Do not create a separate design-system package, stylesheet, component folder, or copied asset set. When an existing build makes its CSS available only under hashed output paths, use those paths and record the required build/preview command in an HTML comment at the top of the file.

## 1. Host the application first

Do not infer the design system from source alone.

1. Inspect `package.json`, the lockfile, framework configuration, entry points, routes, and existing README instructions. Identify the package manager and the existing build/start/preview commands.
2. Install dependencies only through the project's selected package manager when they are missing. Do not replace its tooling, add a bundler, or rewrite scripts.
3. Prefer the production path: run the existing build and host its output using the project's existing preview/serve command. If the project has no production preview command, use its documented development server and say so in the final report.
4. Keep the hosted app available at a browser-accessible URL while inspecting it. A local preview URL is sufficient unless the user explicitly asks for a public deployment. Reuse existing deployment configuration when one is present; do not introduce a hosting provider or publish publicly without an explicit request.
5. Visit the application at desktop and mobile widths, exercise visible states and interactions, and capture the evidence needed to reproduce the system.

If the app cannot be started, diagnose the concrete blocker from the project files and command output. Do not create `design-system.html` from a guess. Report the blocker and the attempted command.

## 2. Analyze the running app and its files

Treat the hosted UI as the authority for rendered appearance and behavior. Use the source to identify reusable markup, classes, assets, variants, and state logic.

Inspect, as applicable:

- app entry points and route tree;
- CSS, CSS Modules, Tailwind configuration, styled-component definitions, and global tokens;
- component files, props, variants, and shared primitives;
- fonts, images, SVG/icon sources, and animation assets;
- existing light/dark themes, responsive breakpoints, and interactive states.

For each candidate element, verify that it is rendered in the hosted app. Include a component, token, state, or motion behavior only when it appears in the running product or is an explicit variant of a rendered shared component. If source and UI disagree, follow the hosted UI and note the discrepancy in an HTML comment.

When React-specific class generation prevents direct reuse (for example CSS Modules), use the class names and stylesheet references emitted by the hosted build. Preserve component markup as rendered HTML. Do not add React, JSX, a runtime bundle, or a second application root to the deliverable.

## 3. Build `design-system.html`

The output is one standalone documentation page in HTML. It reuses the application’s exact classes, assets, fonts, CSS, animations, keyframes, transitions, effects, and layout patterns. Add a small documentation shell only when it can be composed from the application’s existing styles; plain semantic wrappers are acceptable when no matching shell component exists.

### Hard rules

1. Do not redesign, normalize, or invent tokens, components, styles, states, or content types.
2. Reuse exact classes, DOM structure, animation timing/easing, hover/focus states, and responsive behavior whenever they exist.
3. Reference the same emitted CSS/JS assets that make the hosted application look and behave correctly. Do not inline a replacement stylesheet.
4. Never fabricate a hover, active, focus, error, disabled, mobile, or dark state. Omit states that the app does not expose.
5. The page must be self-explanatory through section structure and a top horizontal navigation with anchor links.
6. Do not alter the React application's files except for adding `design-system.html`.

### Required sections

Use only sections supported by the application. Omit an optional section when no relevant element exists.

1. **Hero — required.** Direct clone of the app's primary hero, landing section, or nearest equivalent visible entry region. Preserve markup, classes, images, layout, animation, and interactions. Only its text may change to introduce the design system, with comparable length and hierarchy. If no hero exists, use the app's primary page header and state this in an HTML comment.
2. **Typography — required when text styles exist.** A vertical spec list. Each row contains the style name, a live preview using original element/classes, and its computed `font-size / line-height` label. Include only the rendered hierarchy and weights actually used by the application.
3. **Colors & surfaces.** Show page/section/card surfaces, borders, dividers, overlays, glass effects, and gradients with their real usage context. Use real elements or declared custom properties; do not estimate hex values from screenshots.
4. **Components.** Show each rendered button, input, card, badge, navigation item, dialog, or other reusable primitive once per genuine variant. Present real states side by side only when they are available without inventing them.
5. **Layout & spacing.** Demonstrate two or three actual layout patterns, such as the hero, a content grid, or a split section. Preserve their responsive markup/classes.
6. **Motion & interaction.** Include an interaction gallery only for animations and state changes observed in the hosted app. Retain the original triggers, classes, and timing.
7. **Icons.** If present, display the same icon system with variants and color inheritance that exist in the app.

## 4. Verify

1. Load `design-system.html` through the same hosted environment or an equivalent static server so its relative compiled assets resolve.
2. Compare it with the hosted application at the same desktop and mobile viewports.
3. Verify every asset URL, font, animation, anchor link, hover/focus state, and responsive layout represented on the page.
4. Confirm the output is a single new HTML file and that every showcased item is traceable to the live application.
5. Report the hosted URL, output path, command used to host it, and any real limitations caused by the application build.

## Do not

- Start extraction before the React app is hosted and inspected.
- Replace the app's classes with a new visual system or generic utility classes.
- Copy a screenshot into the page in place of live components.
- Add `package.json`, dependencies, a framework, or generated companion files for the documentation page.
- Claim that a state or behavior exists without observing it in the hosted app or its rendered shared component.
