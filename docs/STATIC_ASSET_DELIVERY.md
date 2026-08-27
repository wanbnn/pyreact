# Static asset delivery

PyReact serves files from `public/` through the same server-driven runtime used by production builds.

## Conditional revalidation

Static files are cacheable but always revalidated before reuse. The runtime sends:

```text
Cache-Control: public, max-age=0, must-revalidate
ETag: W/"..."
```

The ETag is derived from the file modification timestamp and size. A browser or proxy can keep the previously downloaded asset and send its validator back with `If-None-Match`.

If the file is unchanged, PyReact returns:

```text
HTTP/1.1 304 Not Modified
Content-Length: 0
```

The server does not read or retransmit the static file body for that request. This is particularly useful for CSS, JavaScript bundles, fonts, images, and other assets that are reused across navigations.

If the asset changes, its validator changes and the next request returns the new body with `200 OK`. This keeps development and long-running production processes fresh without relying on long immutable cache lifetimes or filename fingerprinting.

Dynamic HTML, event responses, runtime version checks, and server-rendered JSON continue to use `Cache-Control: no-store` because their contents depend on live server state.

## Internal runtime namespace

Paths below `/__pyreact/` are reserved for the browser/runtime protocol and are never shadowed by files in `public/`.

## Deployment notes

A reverse proxy or CDN may honor these validators directly. Applications that fingerprint static filenames at build time can still add a longer-lived cache policy at the edge, but the built-in runtime deliberately chooses revalidation as its safe default so replacing a file in `public/` cannot leave clients stuck on stale content.
