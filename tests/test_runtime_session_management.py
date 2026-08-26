import time

import pytest

from pyreact.runtime import LiveApplication


def _application(tmp_path, **options):
    project = tmp_path / "app"
    source = project / "src"
    public = project / "public"
    source.mkdir(parents=True)
    public.mkdir()
    entry = source / "index.py"
    entry.write_text(
        "from pyreact import h\n"
        "def App(props):\n"
        "    return h('p', None, props['path'])\n",
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
