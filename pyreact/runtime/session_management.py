"""Bounded session lifecycle for the public PyReact live runtime."""

from __future__ import annotations

from http.server import ThreadingHTTPServer
from pathlib import Path
import secrets
import threading
import time
from typing import Dict, Optional

from .server import LiveApplication as _BaseLiveApplication
from .server import LiveSession, make_handler


DEFAULT_SESSION_TTL = 30 * 60.0
DEFAULT_MAX_SESSIONS = 1024


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
            session_id = session_id or secrets.token_urlsafe(24)
            # A caller-provided id may have been evicted as stale or may be new.
            self.sessions[session_id] = LiveSession(self.app)
            self._session_last_seen[session_id] = now
            return session_id, self.sessions[session_id]


def serve(
    entry: str = "src/index.py",
    host: str = "127.0.0.1",
    port: int = 3000,
    public_dir: str = "public",
    title: str = "PyReact App",
    *,
    session_ttl: float = DEFAULT_SESSION_TTL,
    max_sessions: int = DEFAULT_MAX_SESSIONS,
) -> None:
    """Serve a live PyReact app with bounded session retention."""
    application = LiveApplication(
        Path(entry),
        Path(public_dir),
        session_ttl=session_ttl,
        max_sessions=max_sessions,
    )
    server = ThreadingHTTPServer((host, port), make_handler(application, title))
    print(f"[OK] PyReact live server running at http://{host}:{port}", flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
