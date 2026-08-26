# Runtime security limits

PyReact's server-driven runtime keeps component state in Python and receives browser events over `POST /__pyreact/event`. Because these requests are processed by a threaded HTTP server, the public runtime applies explicit resource limits before parsing event payloads.

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

The runtime also bounds retained browser state with `session_ttl` and `max_sessions`. These controls are complementary: session limits bound long-lived server-side state, while `max_event_body_bytes` bounds transient memory accepted from each event request.
