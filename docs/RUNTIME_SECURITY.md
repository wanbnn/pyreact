# Runtime security limits

PyReact's server-driven runtime keeps component state in Python and receives browser events over `POST /__pyreact/event`. Because these requests are processed by a threaded HTTP server, the public runtime applies explicit resource and session-integrity controls before dispatching browser events.

## Session identifier ownership

The public runtime treats the `pyreact_session` cookie only as a reference to an already-existing server session. A cookie value that is unknown, expired, or evicted is never adopted as the identifier for a new session. Instead, PyReact generates a fresh cryptographically random token and returns it in `Set-Cookie`.

This prevents a client from choosing a future server-side session identifier (session fixation) while keeping stale-cookie recovery transparent. Existing valid sessions keep their identifier and refresh their idle deadline normally.

The runtime cookie is always `HttpOnly` and `SameSite=Lax`. For HTTPS deployments, enable the `Secure` attribute explicitly:

```python
from pyreact.runtime import serve

serve(secure_session_cookie=True)
```

The built-in server itself speaks plain HTTP, so `secure_session_cookie` defaults to `False` to keep local development working. In production, it should normally be enabled when TLS is terminated by a reverse proxy or load balancer. Browsers then refuse to send the session cookie over plaintext HTTP, reducing the risk of session disclosure if an insecure route is accidentally exposed.

Do not enable this option for a plain-HTTP deployment: browsers correctly withhold `Secure` cookies on insecure connections, which would create a new session on each request.

## Event request body limit

`pyreact.runtime.serve()` accepts `max_event_body_bytes`. The default is 64 KiB (`65536` bytes):

```python
from pyreact.runtime import serve

serve(max_event_body_bytes=64 * 1024)
```

Requests whose declared `Content-Length` exceeds the configured limit receive HTTP `413 Payload Too Large` before the body is read or a browser session is created. Invalid or negative content lengths receive HTTP `400 Bad Request`.

This turns event-body memory use from a client-controlled, effectively unbounded allocation into a fixed per-request upper bound. Applications that intentionally send larger event payloads can raise the limit explicitly, but should keep it as small as their UI protocol permits.

The limit applies to the public runtime path exposed by `pyreact.runtime.serve()`. Low-level helpers under `pyreact.runtime.server` are implementation details and do not carry the production policy layer.

## Session limits

The runtime also bounds retained browser state with `session_ttl` and `max_sessions`. These controls are complementary: session limits bound long-lived server-side state, server-owned identifiers prevent fixation of that state, `secure_session_cookie` can protect cookie transport in HTTPS deployments, and `max_event_body_bytes` bounds transient memory accepted from each event request.
