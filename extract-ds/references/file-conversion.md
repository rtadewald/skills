# Server-to-`file://` conversion

Read this reference only after the runtime preflight identifies a server
requirement and the user explicitly chooses the slower `file://` conversion.

Preserve the existing project and main animations while adapting only mechanisms
that require an HTTP origin. Work inside `$OUTPUT`; keep `$SOURCE` read-only.

Use the smallest relevant fixes:

- rewrite root-relative paths relative to the copied entry page;
- bundle a required local ES-module graph into browser-ready classic scripts;
- keep remote CDN scripts and fonts when they work from a `null` origin;
- replace blocked local font loading with permitted CDN loading or embedded data;
- replace required local `fetch`/XHR loading for JSON, images, WASM, Rive, GLB,
  HDR, and similar assets with local maps, embedded data, Blob URLs, or an
  equivalent origin-free mechanism;
- adapt Workers, service workers, and WASM initialization only when required by
  the page or a main animation;
- keep navigation inside the copied Overview instead of relying on server routes;
- avoid parent/iframe origin access from Overview.

Production APIs, analytics, tracking, authentication, checkout, secondary routes,
and non-visual backend behavior do not need emulation.

Do not silently fall back to a server. If a protected remote service, DRM, CSP,
or another external restriction makes a main animation genuinely impossible via
`file://`, report the exact blocker and ask whether to preserve the original
server runtime.

The normal verification budget still applies: one browser check and one final
rerun only after a concrete fix. Do not build comparison or screenshot tooling.
