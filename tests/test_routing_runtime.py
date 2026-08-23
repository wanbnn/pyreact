import asyncio
import json
import re
import threading
import time
from pathlib import Path
from urllib.error import HTTPError
from urllib.request import Request, urlopen

import pytest

from pyreact import (
    Link, Navigate, Router, h, match_path, render_to_async_stream,
    render_to_node_stream, render_to_static_node_stream, route, use_location,
    use_params, use_state,
)
from pyreact.dom.dom_operations import CommentNode, Element, TextNode, document
from pyreact.routing import Location, Route, routing_context, set_location
from pyreact.runtime.server import (
    LiveApplication, LiveSession, _document_html, _find_node, make_handler,
    serialize_dom,
)
from http.server import ThreadingHTTPServer


def test_route_matching_location_and_components():
    assert match_path('/', '/') == {}
    assert match_path('/users/:user_id', '/users/42') == {'user_id': '42'}
    assert match_path('/docs/*', '/docs/a/b') == {'wildcard': 'a/b'}
    assert match_path('/a', '/a/more', exact=False) == {}
    assert match_path('/a', '/b') is None

    def User(props):
        assert use_params() == {'user_id': '7'}
        return h('p', None, use_location().pathname)

    with routing_context('/users/7?tab=profile') as location:
        assert location.query == {'tab': ['profile']}
        vnode = Router({'routes': [route('/users/:user_id', User)]})
        assert vnode.type is User and vnode.props['params'] == {'user_id': '7'}

    with routing_context('/missing'):
        assert Router({'routes': []}).children == ['404 — Not Found']
        fallback = h('p', None, 'custom')
        assert Router({'routes': [], 'fallback': fallback}) is fallback
        assert Router({'routes': [], 'fallback': User}).type is User

    explicit = Router({'location': '/users/9', 'routes': [route('/users/:user_id', User)]})
    assert explicit.props['params'] == {'user_id': '9'}
    assert explicit.props['location'].pathname == '/users/9'

    link = Link({'to': '/next', 'className': 'nav', 'children': ['Next']})
    assert link.type == 'a' and link.props['href'] == '/next'
    assert Navigate({'to': '/login'}).type == 'meta'
    assert isinstance(set_location('/search?q=x'), Location)
    assert isinstance(Route('/', User), Route)


def test_invalid_route_parameter():
    with pytest.raises(ValueError, match='Invalid route parameter'):
        match_path('/:bad-name', '/x')


def test_streaming_sync_async_raw_html_and_validation():
    vnode = h('main', None, h('h1', None, 'Title'), h('br'), h('p', None, '<safe>'))
    streamed = ''.join(render_to_node_stream(vnode))
    static = ''.join(render_to_static_node_stream(vnode))
    assert streamed.startswith('<main data-reactroot') and '&lt;safe&gt;' in streamed
    assert 'data-reactroot' not in static

    async def collect():
        return ''.join([chunk async for chunk in render_to_async_stream(vnode)])
    assert asyncio.run(collect()) == streamed
    assert '<b>trusted</b>' in ''.join(render_to_node_stream(
        h('div', {'dangerouslySetInnerHTML': {'__html': '<b>trusted</b>'}})
    ))
    with pytest.raises(ValueError):
        ''.join(render_to_node_stream(h('div', {'dangerouslySetInnerHTML': 'bad'})))


def test_dom_serialization_and_lookup():
    root = Element('div')
    root.attributes.update({'hidden': True, 'skip': False, 'title': '"quoted"'})
    root.style['color'] = 'red'
    root.append_child(TextNode('<text>'))
    child = Element('button')
    child.add_event_listener('click', lambda event: None)
    root.append_child(child)
    html = serialize_dom(root)
    assert 'hidden' in html and 'skip' not in html and '&quot;quoted&quot;' in html
    assert '&lt;text&gt;' in html and 'data-pyreact-path="0.1"' in html
    assert _find_node(root, '0.1') is child
    assert _find_node(root, 'bad') is None and _find_node(root, '0.x') is None
    assert serialize_dom(CommentNode('note')) == '<!--note-->'
    unknown = SimpleNode()
    assert serialize_dom(unknown) == ''

    raw = Element('div')
    raw.set_inner_html('<b>raw</b>')
    assert '<b>raw</b>' in serialize_dom(raw)
    assert '<style' in _document_html('body', 2, '<Title>') or '<title>&lt;Title&gt;</title>' in _document_html('body', 2, '<Title>')


class SimpleNode:
    node_type = 'unknown'


def test_live_session_events_routes_and_errors():
    def App(props):
        count, set_count = use_state(0)
        return h('main', None,
                 h('button', {'onClick': lambda event: set_count(count + 1)}, f'Count {count}'),
                 h('p', None, props['path']))

    session = LiveSession(App)
    html = session.render_path('/first')
    path = re.search(r'data-pyreact-path="([^"]+)"', html).group(1)
    assert '/first' in html
    assert 'Count 1' in session.dispatch(path, 'click', {'type': 'click'})
    with pytest.raises(ValueError):
        session.dispatch(path, 'change', {})
    with pytest.raises(LookupError):
        session.dispatch('0.99', 'click', {})


@pytest.fixture
def live_http_server(tmp_path):
    project = tmp_path / 'app'
    source = project / 'src'
    public = project / 'public'
    source.mkdir(parents=True)
    public.mkdir()
    (public / 'asset.txt').write_text('asset', encoding='utf-8')
    entry = source / 'index.py'
    entry.write_text(
        "from pyreact import h, use_state\n"
        "def App(props):\n"
        "    count, set_count = use_state(0)\n"
        "    return h('button', {'onClick': lambda e: set_count(count + 1)}, f'Count: {count}')\n",
        encoding='utf-8',
    )
    application = LiveApplication(entry, public)
    server = ThreadingHTTPServer(('127.0.0.1', 0), make_handler(application, 'Test App'))
    thread = threading.Thread(target=server.serve_forever, daemon=True)
    thread.start()
    try:
        yield application, entry, f'http://127.0.0.1:{server.server_port}'
    finally:
        server.shutdown()
        server.server_close()
        thread.join(timeout=2)


def _get(url, cookie=None):
    request = Request(url, headers={'Cookie': cookie} if cookie else {})
    return urlopen(request, timeout=3)


def test_live_http_protocol_static_navigation_events_and_reload(live_http_server):
    application, entry, base = live_http_server
    with _get(base + '/') as response:
        page = response.read().decode()
        cookie = response.headers['Set-Cookie'].split(';', 1)[0]
    assert '<title>Test App</title>' in page and 'Count: 0' in page
    path = re.search(r'data-pyreact-path="([^"]+)"', page).group(1)

    payload = json.dumps({'path': path, 'type': 'click', 'payload': {'type': 'click'}}).encode()
    request = Request(base + '/__pyreact/event', data=payload,
                      headers={'Content-Type': 'application/json', 'Cookie': cookie})
    with urlopen(request, timeout=3) as response:
        assert 'Count: 1' in json.loads(response.read())['html']

    with _get(base + '/__pyreact/render?path=%2Fabout', cookie) as response:
        assert response.status == 200
    with _get(base + '/__pyreact/runtime.js') as response:
        assert b'data-pyreact-events' in response.read()
    with _get(base + '/asset.txt') as response:
        assert response.read() == b'asset'
    with _get(base + '/__pyreact/version') as response:
        old_version = json.loads(response.read())['version']

    time.sleep(0.02)
    entry.write_text(entry.read_text() + '\n# reload\n', encoding='utf-8')
    with _get(base + '/__pyreact/version') as response:
        assert json.loads(response.read())['version'] == old_version + 1
    assert application.version == old_version + 1

    bad = Request(base + '/__pyreact/event', data=b'{}', headers={'Cookie': cookie})
    with pytest.raises(HTTPError) as error:
        urlopen(bad, timeout=3)
    assert error.value.code == 400
    missing = Request(base + '/missing-endpoint', data=b'{}')
    with pytest.raises(HTTPError) as error:
        urlopen(missing, timeout=3)
    assert error.value.code == 404
