# Component formats

Read this file only during Phase 2, after Overview has been approved. Keep the
extraction copy-first and source-backed: every value and live specimen must come
directly from the approved Overview.

Make one quick pass through visible markup and source styles. Do not measure the
page at multiple viewport widths, sweep computed styles, search for hidden
variants, calculate contrast, or inventory unused declarations.

## Typography

Order clearly distinct type styles from strongest to smallest. Render one
horizontal row per style, separated by subtle dividers, using the same fixed
three-part presentation throughout:

1. **Left:** observed role (`Heading 1`, `Text 1`, `Button`, `Meta`, or similar),
   followed only by the original font family and weight.
2. **Center:** a large live sample using the Overview's original inner HTML,
   class, and styling, including spans, gradients, colors, tracking, transforms,
   effects, and line breaks.
3. **Right:** the existing `font-size` value declared in source CSS, aligned with
   the row. If responsive sizes are already explicit in the CSS, list those
   values from widest to narrowest separated by ` | `. If only one size is
   declared, show only that value.

Keep the left, center, and right columns consistently aligned across every row,
with the center specimen receiving most of the width. Store the selector or
class as compact code metadata without disturbing this presentation. Do not
render multiple viewports or measure font sizes from screenshots or browser
geometry.

## Colors

Present colors by their observed function, not as one undifferentiated palette.
Create only groups supported by Overview. Use these names when applicable:

- Brand and Accent;
- Surfaces;
- Text and Icons;
- Borders;
- Semantic;
- Interactive States; and
- Overlays.

Each color item contains:

1. a live swatch shown on the surface where the color is used;
2. an evidence-based functional label, such as `Primary text` or
   `Elevated surface`;
3. its exact active CSS value;
4. its original token name when the source defines one; and
5. one short observed use.

A functional label is documentation, not a source token. If the source defines
no token, show only the label and value; never invent token names.

Keep related interaction colors together as one state family, ordered `Default |
Hover | Active | Selected | Disabled | Focus`, including only states already
visible, reachable, or explicit in source CSS. Document light and dark modes
only when both are implemented.

Preserve opacity for translucent colors and show overlays on their real
underlying surface. The same value may appear more than once when it serves
different observed roles.

Do not calculate contrast, sweep computed styles, inspect unused palette
declarations, invent semantic meanings, or search for hidden states.

## Backgrounds

Create this group whenever Overview contains one or more backgrounds, even when
there is only one. Use the principal animated background as the live background
of the whole Components view. If none is animated, use the principal observed
static background.

Also show every distinct observed background as a large live specimen in this
group. Reuse its real HTML, CSS, canvas, WebGL, video, scripts, assets, layers,
overlays, and animation. Preserve source sizing and composition closely enough
for the background to be judged on its own. Do not replace it with a screenshot,
poster frame, gradient approximation, or newly invented variant.

When multiple specimens share the same underlying implementation, reuse it with
the observed source configuration instead of duplicating or reverse-engineering
the animation.

## Surfaces

Show each clearly recurring surface live on the background where it is used.
Preserve its source opacity, blur, border, mask, shadow, glow, and layers. Keep
gradients inside their actual surface or background rather than creating a
separate Gradients group.

## Icons

Render original icons directly, without enclosing each icon in a decorative
card. Use a simple aligned grid, five items per row when space allows. Keep each
identifier or class immediately below its icon. Preserve source size, color,
fill, stroke, and reachable state; do not substitute another icon library.

## Complete components

Document complete reusable units clearly visible in Overview. Classify them by
their observed function only when grouping helps navigation, for example:

- Actions;
- Navigation;
- Inputs and forms;
- Cards and containers;
- Data display and visualization;
- Feedback and status;
- Overlays and disclosure;
- Content groups;
- Media;
- Search, filtering, and controls; or
- Domain-specific components.

Do not create empty categories or document every internal HTML element as a
component. Group repeated instances as one family with only observed variants.

## Specimen format

Render the live component using its Overview HTML, CSS, copy, assets, and
required context. Keep supporting information directly aligned with the item it
describes. Include only useful observed information:

- functional name;
- live component;
- selector, class, token, or source;
- real variants or reachable states; and
- essential context or behavior.

Do not add empty anatomy sections, verbose provenance, invented states, or an
outer card when the component already has its own visible boundary.
