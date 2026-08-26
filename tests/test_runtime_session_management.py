import json
import re
import threading
import time
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from pyreact.runtime import DEFAULT_MAX_EVENT_BODY_BYTES, LiveApplication
from pyreact.runtime.session_management import make_handler


def _application(tmp_path, **options):
    project = tmp_path / "app"
    source = project / "src"
    public = project / "public"
    source.mkdir(parents=True)
    public.mkdir()
    entry = source / "index.py"
    entry.write_text(
        "from pyreact import h, use_state\n"
        "def App(props):\n"
        "    count, set_count = use_state(0)\n"
        "    return h('button', {'onClick': lambda e: set_count(count + 1)}, f'Count: {count}')\n",
        encoding="utf-8",
    )
    return LiveApplication(entry, public, **options)


def test_live_sessions_have_a_hard_capacity_and_evict_lru(tmp_path):
    application = _application(tmp_path, max_sessions=2, session_ttl=3600)

    _, first = application.session("first")
    application.session("second")
    # Refresh the first session so the second becomes least recently used.
    refreshed_id, refreshed = application.session("first")
    assert refreshed_id == "first"
    assert refreshed is first

    application.session("third")

    assert len(application.sessions) == 2
    assert set(application.sessions) == {"first", "third"}
    assert "second" not in application._session_last_seen


def test_idle_sessions_expire_before_new_sessions_are_created(tmp_path):
    application = _application(tmp_path, max_sessions=10, session_ttl=30)
    _, expired = application.session("expired")
    application.session("active")
    application._session_last_seen["expired"] = time.monotonic() - 31

    application.session("new")

    assert "expired" not in application.sessions
    assert "expired" not in application._session_last_seen
    assert set(application.sessions) == {"active", "new"}
    _, replacement = application.session("expired")
    assert replacement is not expired


def test_session_access_refreshes_idle_deadline(tmp_path):
    application = _application(tmp_path, session_ttl=30)
    _, session = application.session("browser")
    application._session_last_seen["browser"] = time.monotonic() - 29

    _, refreshed = application.session("browser")

    assert refreshed is session
    assert time.monotonic() - application._session_last_seen["browser"] < 1


def test_session_limits_are_validated(tmp_path):
    with pytest.raises(ValueError, match="session_ttl"):
        _application(tmp_path / "ttl", session_ttl=0)
    with pytest.raises(ValueError, match="max_sessions"):
        _application(tmp_path / "capacity", max_sessions=0)


def _start_server(application, *, max_event_body_bytes):
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        make_handler(
            application,
            "Security Test",
            max_event_body_bytes=max_event_body_bytes,
        ),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def test_event_body_limit_is_positive(tmp_path):
    application = _application(tmp_path)
    with pytest.raises(ValueError, match="max_event_body_bytes"):
        make_handler(application, max_event_body_bytes=0)
    assert DEFAULT_MAX_EVENT_BODY_BYTES == 64 * 1024


def test_oversized_event_is_rejected_before_session_creation(tmp_path):
    application = _application(tmp_path)
    server, thread, base = _start_server(application, max_event_body_bytes=64)
    try:
        body = json.dumps(
            {"path": "0", "type": "click", "payload": {"value": "x" * 256}}
        ).encode()
        request = Request(
            base + "/__pyreact/event",
            data=body,
            headers={"Content-Type": "application/json"},
        )
        with pytest.raises(HTTPError) as error:
            urlopen(request, timeout=3)
        assert error.value.code == 413
        payload = json.loads(error.value.read())
        assert "64 bytes" in payload["error"]
        assert application.sessions == {}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_event_under_limit_preserves_protocol(tmp_path):
    application = _application(tmp_path)
    server, thread, base = _start_server(application, max_event_body_bytes=1024)
    try:
        with urlopen(base + "/", timeout=3) as response:
            page = response.read().decode()
            cookie = response.headers["Set-Cookie"].split(";", 1)[0]
        path = re.search(r'data-pyreact-path="([^"]+)"', page).group(1)
        body = json.dumps(
            {"path": path, "type": "click", "payload": {"type": "click"}}
        ).encode()
        request = Request(
            base + "/__pyreact/event",
            data=body,
            headers={"Content-Type": "application/json", "Cookie": cookie},
        )
        with urlopen(request, timeout=3) as response:
            payload = json.loads(response.read())
        assert "Count: 1" in payload["html"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
