import json
import re
import threading
from http.server import ThreadingHTTPServer
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from pyreact.runtime import LiveApplication
from pyreact.runtime.session_management import make_handler


def _application(tmp_path):
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
    return LiveApplication(entry, public)


def _start_server(application):
    server = ThreadingHTTPServer(
        ("127.0.0.1", 0),
        make_handler(application, "Origin Test", max_event_body_bytes=1024),
    )
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    return server, thread, f"http://127.0.0.1:{server.server_port}"


def _event_request(base, body, **headers):
    return Request(
        base + "/__pyreact/event",
        data=body,
        headers={"Content-Type": "application/json", **headers},
    )


def test_cross_origin_event_is_rejected_before_session_creation(tmp_path):
    application = _application(tmp_path)
    server, thread, base = _start_server(application)
    try:
        body = json.dumps(
            {"path": "0", "type": "click", "payload": {"type": "click"}}
        ).encode()
        request = _event_request(base, body, Origin="https://evil.example")

        with pytest.raises(HTTPError) as error:
            urlopen(request, timeout=3)

        assert error.value.code == 403
        assert "Cross-origin" in json.loads(error.value.read())["error"]
        assert application.sessions == {}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_same_site_sibling_context_is_rejected_by_fetch_metadata(tmp_path):
    application = _application(tmp_path)
    server, thread, base = _start_server(application)
    try:
        body = json.dumps(
            {"path": "0", "type": "click", "payload": {"type": "click"}}
        ).encode()
        request = _event_request(
            base,
            body,
            **{"Sec-Fetch-Site": "same-site"},
        )

        with pytest.raises(HTTPError) as error:
            urlopen(request, timeout=3)

        assert error.value.code == 403
        assert application.sessions == {}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_malformed_origin_is_rejected(tmp_path):
    application = _application(tmp_path)
    server, thread, base = _start_server(application)
    try:
        body = b"{}"
        request = _event_request(base, body, Origin="null")

        with pytest.raises(HTTPError) as error:
            urlopen(request, timeout=3)

        assert error.value.code == 403
        assert application.sessions == {}
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def test_same_origin_browser_event_preserves_protocol(tmp_path):
    application = _application(tmp_path)
    server, thread, base = _start_server(application)
    try:
        with urlopen(base + "/", timeout=3) as response:
            page = response.read().decode()
            cookie = response.headers["Set-Cookie"].split(";", 1)[0]
        path = re.search(r'data-pyreact-path="([^"]+)"', page).group(1)
        body = json.dumps(
            {"path": path, "type": "click", "payload": {"type": "click"}}
        ).encode()
        request = _event_request(
            base,
            body,
            Origin=base,
            Cookie=cookie,
            **{"Sec-Fetch-Site": "same-origin"},
        )

        with urlopen(request, timeout=3) as response:
            payload = json.loads(response.read())

        assert "Count: 1" in payload["html"]
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)
