# Component formats

Read this file only during Step 5, after Overview has been approved. Apply a
section only when that group is observed in Overview. Every example must be live
HTML/CSS and traceable to Overview; never invent names, values, states, or
variants.

## Typography

Order observed styles from strongest to smallest and render one row per style,
separated by subtle dividers. Each row has three areas:

1. Left: observed role (`Heading 1`, `Text 1`, `Button`, `Meta`, or similar),
   then only font family and weight.
2. Center: real Overview copy with its original inner HTML and computed style,
   including spans, gradients, colors, tracking, transforms, and line breaks.
3. Right: three measured `font-size` values, widest to narrowest, formatted as
   `64px | 64px | 44px` without viewport labels or line height.

Measure at 1440px, 1024px, and 390px unless the source establishes better
reference widths. Repeat unchanged values; never infer a progression. Keep line
height, tracking, color, selector, and measurement widths applied to the example
or in code metadata without making the visible row verbose.

## Colors

Present color by observed function, not as one undifferentiated palette. 

Create only groups supported by Overview. Use these names when applicable:

- Brand and Accent;
- Surfaces;
- Text and Icons;
- Borders;
- Semantic;
- Interactive States; and
- Overlays.

Each color item contains:

1. a live swatch rendered over the background on which the color is used;
2. an evidence-based functional label, such as `Primary text` or
   `Elevated surface`;
3. its exact active CSS value;
4. its original token name when the source defines one; and
5. one short observed use.

A functional label describes documentation; it is not a source token. Never
present an invented name such as `text.primary` as code. If the source has no
token, show the functional label and value without fabricating one.

Keep related interaction colors together as one state family, ordered `Default |
Hover | Active | Selected | Disabled | Focus`, including only observed states.
Document light and dark modes only when both are implemented. For text and icon
roles, show the measured contrast against their actual recurring surface when
the pairing is unambiguous. Preserve opacity for translucent colors and show
overlays on their real underlying surface.

The same pigment may appear more than once when it has distinct observed roles.
Omit declared but unused colors, empty groups, speculative semantic meanings,
and states that cannot be reached in Overview.

## Surfaces

Show each shared surface live on its correct surrounding background, with its
active CSS composition and one observed use. Preserve the layers, opacity, blur,
borders, masks, shadows, glow, and other effects that produce the surface.
Gradients may appear as part of that composition, but never create a separate
Gradients group.


## Icons

Render each original icon at its observed size and color. Show its existing
identifier, dimensions, and use. Preserve fill, stroke, `currentColor`, and
observed interactive states. Do not substitute another icon library.

## Motion

Use the real component containing the motion. Show the observed trigger,
duration, easing, and animated property from the source. Do not create a demo
animation when none exists.

## Component taxonomy

Classify complete components by their primary observed function. Create only
categories represented in Overview. A component may use elements from another
category internally; classify the complete reusable unit, not every HTML tag it
contains.

### Actions

Buttons, icon buttons, button groups, split buttons, floating actions, text
links, inline links, and download or share actions.

### Navigation

Navbars, headers, sidebars, navigation rails, tabs, breadcrumbs, pagination,
steppers, tables of contents, menus, previous/next controls, and anchor
navigation.

### Inputs and forms

Text, password, number, search, and multiline fields; selects, comboboxes,
autocomplete, checkboxes, radios, switches, sliders, date/time controls, file
uploads, field labels, helper text, validation messages, form groups, and form
actions.

### Cards and containers

Basic, interactive, feature, article, product, pricing, profile, statistic,
media, action, and expandable cards; dashboard panels, widgets, and recurring
list-item containers. Treat matching cards as one family with observed variants.

### Data display

Tables, data grids, lists, description lists, key-value rows, statistics, KPIs,
badges, tags, chips, status indicators, avatars, timelines, calendars, code
blocks, metadata groups, ratings, counters, and progress values.

### Charts and data visualization

Line, bar, area, pie, donut, scatter, radar, heatmap, gauge, and sparkline charts;
progress graphics, maps, diagrams, legends, axes, chart labels, tooltips, and
chart controls. Prefer documenting a chart as one complete component, with axes,
legends, and tooltips as its anatomy unless they recur independently.

### Feedback and status

Alerts, banners, toasts, snackbars, inline feedback, success, error, warning and
information states, loaders, spinners, skeletons, progress indicators, empty or
offline states, and connection or status indicators.

### Overlays and disclosure

Dialogs, modals, drawers, sheets, popovers, tooltips, dropdowns, context menus,
accordions, disclosures, collapsible panels, lightboxes, and hover cards.

### Content and text groups

Hero copy, section headings, eyebrow/title/description groups, feature
descriptions, label/value pairs, quotes, testimonials, callouts, article headers,
captions, legal groups, metadata rows, FAQ items, and CTA blocks. Isolated type
styles belong to Typography; recurring combinations of type styles are
components.

### Media

Images, video or audio players, thumbnails, galleries, carousels, image
comparisons, figures with captions, logos, logo clouds, illustration containers,
maps, media viewports, and embeds.

### Search, filter, and sorting

Search bars, filters, filter groups or chips, faceted filters, sort selectors,
result counts, active-filter summaries, clear-filter actions, view switchers,
and command palettes.

### Selection and control

Segmented controls, toggle groups, toolbars, zoom or directional controls,
playback controls, quantity selectors, view or theme selectors, drag handles,
and resize handles.

### Identity and account

Profiles, account or avatar menus, organization switchers, authentication forms,
user-status displays, and notification controls.

### Domain-specific components

Reusable units whose real function does not fit the categories above, such as a
telemetry panel, mission status, financial ticker, product configurator, code
editor, terminal, music player, booking selector, or scientific instrument. Use
the function and name evidenced by Overview instead of forcing a generic label.

## Component specimen format

Render each component with the Overview's live HTML, CSS, copy, and assets. A
specimen may document:

1. its evidence-based functional name;
2. the live component;
3. observed anatomy;
4. observed variants;
5. reachable states;
6. behavior and interaction;
7. dimensions or context essential to its appearance; and
8. its selector or source in code metadata.

Show only applicable information. Do not create empty anatomy, variants, or
states sections. Preserve the context required by effects, and group repeated
instances instead of duplicating identical specimens.
