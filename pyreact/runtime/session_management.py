"""Bounded session and request lifecycle for the public PyReact live runtime."""

from __future__ import annotations

from http import HTTPStatus
from http.server import ThreadingHTTPServer
from pathlib import Path
import secrets
import threading
import time
from typing import Dict, Optional
from urllib.parse import urlsplit

from .server import LiveApplication as _BaseLiveApplication
from .server import LiveSession, make_handler as _base_make_handler


DEFAULT_SESSION_TTL = 30 * 60.0
DEFAULT_MAX_SESSIONS = 1024
DEFAULT_MAX_EVENT_BODY_BYTES = 64 * 1024


class LiveApplication(_BaseLiveApplication):
    """Live application with bounded, idle-expiring browser sessions.

    ``session_ttl`` controls how long an inactive session is retained, while
    ``max_sessions`` provides a hard memory bound. Once the limit is reached,
    the least-recently-used session is evicted before a new one is created.
    """

    def __init__(
        self,
        entry: Path,
        public_dir: Optional[Path] = None,
        *,
        session_ttl: float = DEFAULT_SESSION_TTL,
        max_sessions: int = DEFAULT_MAX_SESSIONS,
    ):
        if session_ttl <= 0:
            raise ValueError("session_ttl must be greater than zero")
        if max_sessions < 1:
            raise ValueError("max_sessions must be at least one")
        self.session_ttl = float(session_ttl)
        self.max_sessions = int(max_sessions)
        self._session_last_seen: Dict[str, float] = {}
        self._sessions_lock = threading.RLock()
        super().__init__(entry, public_dir)

    def _evict_expired(self, now: float) -> int:
        expired = [
            session_id
            for session_id, last_seen in self._session_last_seen.items()
            if now - last_seen >= self.session_ttl
        ]
        for session_id in expired:
            self.sessions.pop(session_id, None)
            self._session_last_seen.pop(session_id, None)
        return len(expired)

    def _evict_lru_if_full(self) -> None:
        if len(self.sessions) < self.max_sessions:
            return
        oldest = min(self._session_last_seen, key=self._session_last_seen.__getitem__)
        self.sessions.pop(oldest, None)
        self._session_last_seen.pop(oldest, None)

    def _new_session_id(self) -> str:
        while True:
            session_id = secrets.token_urlsafe(24)
            if session_id not in self.sessions:
                return session_id

    def reload_if_changed(self) -> bool:
        with self._sessions_lock:
            changed = super().reload_if_changed()
            if changed:
                self._session_last_seen.clear()
            return changed

    def session(self, session_id: Optional[str] = None) -> tuple[str, LiveSession]:
        now = time.monotonic()
        with self._sessions_lock:
            self._evict_expired(now)
            if session_id and session_id in self.sessions:
                self._session_last_seen[session_id] = now
                return session_id, self.sessions[session_id]

            self._evict_lru_if_full()
            # Never let an unknown or stale client cookie choose the identifier
            # of a server-side session. Rotating it to a fresh random token
            # prevents session fixation while transparently recovering expired
            # or invalid browser sessions.
            session_id = self._new_session_id()
            self.sessions[session_id] = LiveSession(self.app)
            self._session_last_seen[session_id] = now
            return session_id, self.sessions[session_id]


def make_handler(
    application: LiveApplication,
    title: str = "PyReact App",
    *,
    max_event_body_bytes: int = DEFAULT_MAX_EVENT_BODY_BYTES,
):
    """Create a runtime handler that bounds browser event request bodies.

    The lower-level live server historically trusted ``Content-Length`` and
    read that many bytes into memory. The public runtime rejects oversized or
    malformed lengths before delegating to the event parser, keeping memory
    consumed by each event request bounded independently of client input.
    """
    if max_event_body_bytes < 1:
        raise ValueError("max_event_body_bytes must be at least one")

    base_handler = _base_make_handler(application, title)

    class BoundedEventHandler(base_handler):
        def do_POST(self) -> None:
            if urlsplit(self.path).path == "/__pyreact/event":
                raw_length = self.headers.get("Content-Length")
                try:
                    length = int(raw_length or "0")
                except ValueError:
                    self._json(
                        {"error": "Invalid Content-Length"},
                        HTTPStatus.BAD_REQUEST,
                    )
                    return
                if length < 0:
                    self._json(
                        {"error": "Invalid Content-Length"},
                        HTTPStatus.BAD_REQUEST,
                    )
                    return
                if length > max_event_body_bytes:
                    self._json(
                        {
                            "error": (
                                "Event payload exceeds the configured limit of "
                                f"{max_event_body_bytes} bytes"
                            )
                        },
                        HTTPStatus.REQUEST_ENTITY_TOO_LARGE,
                    )
                    return
            super().do_POST()

    return BoundedEventHandler


def serve(
    entry: str = "src/index.py",
    host: str = "127.0.0.1",
    port: int = 3000,
    public_dir: str = "public",
    title: str = "PyReact App",
    *,
    session_ttl: float = DEFAULT_SESSION_TTL,
    max_sessions: int = DEFAULT_MAX_SESSIONS,
    max_event_body_bytes: int = DEFAULT_MAX_EVENT_BODY_BYTES,
) -> None:
    """Serve a live PyReact app with bounded sessions and event requests."""
    application = LiveApplication(
        Path(entry),
        Path(public_dir),
        session_ttl=session_ttl,
        max_sessions=max_sessions,
    )
    server = ThreadingHTTPServer(
        (host, port),
        make_handler(
            application,
            title,
            max_event_body_bytes=max_event_body_bytes,
        ),
    )
    print(f"[OK] PyReact live server running at http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
