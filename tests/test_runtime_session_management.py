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

    first_id, first = application.session()
    second_id, _ = application.session()
    # Refresh the first session so the second becomes least recently used.
    refreshed_id, refreshed = application.session(first_id)
    assert refreshed_id == first_id
    assert refreshed is first

    third_id, _ = application.session()

    assert len(application.sessions) == 2
    assert set(application.sessions) == {first_id, third_id}
    assert second_id not in application._session_last_seen


def test_idle_sessions_expire_and_rotate_their_identifier(tmp_path):
    application = _application(tmp_path, max_sessions=10, session_ttl=30)
    expired_id, expired = application.session()
    active_id, _ = application.session()
    application._session_last_seen[expired_id] = time.monotonic() - 31

    new_id, _ = application.session()

    assert expired_id not in application.sessions
    assert expired_id not in application._session_last_seen
    assert set(application.sessions) == {active_id, new_id}
    replacement_id, replacement = application.session(expired_id)
    assert replacement_id != expired_id
    assert replacement is not expired
    assert expired_id not in application.sessions


def test_session_access_refreshes_idle_deadline(tmp_path):
    application = _application(tmp_path, session_ttl=30)
    browser_id, session = application.session()
    application._session_last_seen[browser_id] = time.monotonic() - 29

    refreshed_id, refreshed = application.session(browser_id)

    assert refreshed_id == browser_id
    assert refreshed is session
    assert time.monotonic() - application._session_last_seen[browser_id] < 1


def test_unknown_client_session_id_is_never_adopted(tmp_path, monkeypatch):
    application = _application(tmp_path)
    generated = iter(["server-generated-session"])
    monkeypatch.setattr(
        "pyreact.runtime.session_management.secrets.token_urlsafe",
        lambda _: next(generated),
    )

    session_id, _ = application.session("attacker-chosen-session")

    assert session_id == "server-generated-session"
    assert "attacker-chosen-session" not in application.sessions
    assert set(application.sessions) == {"server-generated-session"}


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


def test_forged_session_cookie_is_rotated_by_http_runtime(tmp_path):
    application = _application(tmp_path)
    server, thread, base = _start_server(application, max_event_body_bytes=1024)
    try:
        request = Request(
            base + "/",
            headers={"Cookie": "pyreact_session=attacker-chosen-session"},
        )
        with urlopen(request, timeout=3) as response:
            cookie = response.headers["Set-Cookie"].split(";", 1)[0]
        assigned_id = cookie.split("=", 1)[1]

        assert assigned_id != "attacker-chosen-session"
        assert "attacker-chosen-session" not in application.sessions
        assert assigned_id in application.sessions
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
