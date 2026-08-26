"""A dependency-free live server that executes PyReact applications in Python."""

from html import escape
from http import HTTPStatus
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import importlib.util
import json
import mimetypes
from pathlib import Path
import secrets
import sys
import threading
from typing import Any, Callable, Dict, Optional
from urllib.parse import parse_qs, urlsplit

from ..core.element import VNode, h
from ..core.renderer import render
from ..dom.dom_operations import DOMNode, Element, dispatch_event, document
from ..routing import routing_context
from ..server.ssr import VOID_ELEMENTS


def serialize_dom(node: DOMNode, path: str = '0') -> str:
    """Serialize the in-memory DOM and annotate interactive nodes."""
    if node.node_type == 'text':
        return escape(str(node.text_content), quote=False)
    if node.node_type == 'comment':
        return f'<!--{escape(str(node.text_content), quote=False)}-->'
    if not isinstance(node, Element):
        return ''

    attributes = []
    for name, value in node.attributes.items():
        if value is False or value is None:
            continue
        if value is True:
            attributes.append(escape(str(name), quote=True))
        else:
            attributes.append(
                f'{escape(str(name), quote=True)}="{escape(str(value), quote=True)}"'
            )
    if node.style:
        style = ';'.join(f'{name}:{value}' for name, value in node.style.items())
        attributes.append(f'style="{escape(style, quote=True)}"')
    if node._event_listeners:
        attributes.append(f'data-pyreact-path="{path}"')
        events = ','.join(sorted(node._event_listeners))
        attributes.append(f'data-pyreact-events="{escape(events, quote=True)}"')
    attr_text = (' ' + ' '.join(attributes)) if attributes else ''
    if node.tag_name in VOID_ELEMENTS:
        return f'<{node.tag_name}{attr_text}>'
    if node._raw_inner_html:
        content = node._text_content
    else:
        prefix = escape(node._text_content, quote=False)
        content = prefix + ''.join(
            serialize_dom(child, f'{path}.{index}')
            for index, child in enumerate(node.child_nodes)
        )
    return f'<{node.tag_name}{attr_text}>{content}</{node.tag_name}>'


def _find_node(root: DOMNode, path: str) -> Optional[Element]:
    parts = path.split('.')
    if not parts or parts[0] != '0':
        return None
    node: DOMNode = root
    for part in parts[1:]:
        try:
            node = node.child_nodes[int(part)]
        except (ValueError, IndexError):
            return None
    return node if isinstance(node, Element) else None


class LiveSession:
    """A persistent component tree and state container for one browser session."""

    def __init__(self, app: Callable[[Dict[str, Any]], VNode], path: str = '/'):
        self.app = app
        self.path = path
        self.container = document.create_element('div')
        self.root = None
        self._lock = threading.RLock()

    def render_path(self, path: str) -> str:
        with self._lock, routing_context(path):
            self.path = path
            vnode = h(self.app, {'path': path})
            if self.root is None:
                self.root = render(vnode, self.container)
            else:
                self.root.render(vnode)
            return self.html

    @property
    def html(self) -> str:
        return ''.join(serialize_dom(child, str(index)) for index, child in enumerate(
            self.container.child_nodes
        ))

    def dispatch(self, path: str, event_type: str, payload: Dict[str, Any]) -> str:
        with self._lock, routing_context(self.path):
            if not self.container.first_child:
                self.render_path(self.path)
            node = _find_node(self.container.first_child, path)
            if node is None:
                raise LookupError(f'Interactive node {path!r} no longer exists')
            if event_type not in node._event_listeners:
                raise ValueError(f'Event {event_type!r} is not registered for node {path!r}')
            dispatch_event(node, event_type, payload)
            return self.html


class LiveApplication:
    """Loads an entry module, owns browser sessions and tracks source changes."""

    def __init__(self, entry: Path, public_dir: Optional[Path] = None):
        self.entry = entry.resolve()
        self.project_dir = self.entry.parent.parent
        self.public_dir = (public_dir or self.project_dir / 'public').resolve()
        self.sessions: Dict[str, LiveSession] = {}
        self.version = 1
        self._source_stamp = 0.0
        self.app = self._load_app()

    def _latest_source_stamp(self) -> float:
        source_root = self.project_dir / 'src'
        files = source_root.rglob('*.py') if source_root.exists() else [self.entry]
        return max((path.stat().st_mtime for path in files), default=self.entry.stat().st_mtime)

    def _load_app(self) -> Callable[[Dict[str, Any]], VNode]:
        project_text = str(self.project_dir)
        if project_text not in sys.path:
            sys.path.insert(0, project_text)
        # Imported application modules must not survive a hot reload.
        for name, loaded in list(sys.modules.items()):
            module_file = getattr(loaded, '__file__', None)
            if name.startswith('pyreact') or not module_file:
                continue
            try:
                Path(module_file).resolve().relative_to(self.project_dir)
            except ValueError:
                continue
            sys.modules.pop(name, None)
        module_name = f'_pyreact_app_{secrets.token_hex(6)}'
        spec = importlib.util.spec_from_file_location(module_name, self.entry)
        if spec is None or spec.loader is None:
            raise ImportError(f'Cannot load PyReact entry point: {self.entry}')
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        candidate = getattr(module, 'app', None) or getattr(module, 'App', None)
        if not callable(candidate):
            raise AttributeError('Entry module must export a callable named app or App')
        self._source_stamp = self._latest_source_stamp()
        return candidate

    def reload_if_changed(self) -> bool:
        stamp = self._latest_source_stamp()
        if stamp <= self._source_stamp:
            return False
        self.app = self._load_app()
        self.sessions.clear()
        self.version += 1
        return True

    def session(self, session_id: Optional[str] = None) -> tuple[str, LiveSession]:
        session_id = session_id or secrets.token_urlsafe(24)
        if session_id not in self.sessions:
            self.sessions[session_id] = LiveSession(self.app)
        return session_id, self.sessions[session_id]


_BROWSER_RUNTIME = r'''(() => {
  const root = document.getElementById('root');
  let version = Number(document.documentElement.dataset.pyreactVersion || '1');
  let pending = Promise.resolve();

  const cloneInto = (parent, nextNode, before = null) => {
    const clone = nextNode.cloneNode(true);
    parent.insertBefore(clone, before);
    return clone;
  };

  const syncFormState = (current, next) => {
    if (current instanceof HTMLInputElement && next instanceof HTMLInputElement) {
      if (next.hasAttribute('value') && current.value !== next.value) current.value = next.value;
      if (current.checked !== next.checked) current.checked = next.checked;
    } else if (current instanceof HTMLTextAreaElement && next instanceof HTMLTextAreaElement) {
      if (current.value !== next.value) current.value = next.value;
    } else if (current instanceof HTMLSelectElement && next instanceof HTMLSelectElement) {
      if (current.value !== next.value) current.value = next.value;
    }
  };

  const syncAttributes = (current, next) => {
    for (const attribute of Array.from(current.attributes)) {
      if (!next.hasAttribute(attribute.name)) current.removeAttribute(attribute.name);
    }
    for (const attribute of Array.from(next.attributes)) {
      if (current.getAttribute(attribute.name) !== attribute.value) {
        current.setAttribute(attribute.name, attribute.value);
      }
    }
    syncFormState(current, next);
  };

  const patchNode = (current, next) => {
    if (current.nodeType !== next.nodeType || current.nodeName !== next.nodeName) {
      const replacement = next.cloneNode(true);
      current.replaceWith(replacement);
      return replacement;
    }

    if (current.nodeType === Node.TEXT_NODE || current.nodeType === Node.COMMENT_NODE) {
      if (current.nodeValue !== next.nodeValue) current.nodeValue = next.nodeValue;
      return current;
    }

    if (!(current instanceof Element) || !(next instanceof Element)) return current;
    syncAttributes(current, next);

    let index = 0;
    while (index < next.childNodes.length || index < current.childNodes.length) {
      const currentChild = current.childNodes[index];
      const nextChild = next.childNodes[index];
      if (!nextChild && currentChild) {
        currentChild.remove();
        continue;
      }
      if (nextChild && !currentChild) {
        cloneInto(current, nextChild);
        index += 1;
        continue;
      }
      patchNode(currentChild, nextChild);
      index += 1;
    }
    return current;
  };

  const apply = (payload) => {
    if (typeof payload.html !== 'string') return;
    const template = document.createElement('template');
    template.innerHTML = payload.html;
    const nextRoot = template.content;

    let index = 0;
    while (index < nextRoot.childNodes.length || index < root.childNodes.length) {
      const currentChild = root.childNodes[index];
      const nextChild = nextRoot.childNodes[index];
      if (!nextChild && currentChild) {
        currentChild.remove();
        continue;
      }
      if (nextChild && !currentChild) {
        cloneInto(root, nextChild);
        index += 1;
        continue;
      }
      patchNode(currentChild, nextChild);
      index += 1;
    }
  };

  const enqueue = (operation) => {
    pending = pending.then(operation, operation);
    return pending;
  };
  function sendEvent(node, type, event) {
    const target = event.target || node;
    const payload = {type, key: event.key || '', code: event.code || '',
      target: {value: target.value ?? '', checked: Boolean(target.checked)}};
    const body = JSON.stringify({path: node.dataset.pyreactPath, type, payload});
    return enqueue(async () => {
      const response = await fetch('/__pyreact/event', {method: 'POST',
        headers: {'Content-Type': 'application/json'}, body});
      if (!response.ok) throw new Error(await response.text());
      apply(await response.json());
    });
  }
  for (const type of ['click','change','input','submit','keydown','keyup','focus','blur']) {
    document.addEventListener(type, (event) => {
      const link = event.target.closest?.('a[data-pyreact-link]');
      if (type === 'click' && link) {
        event.preventDefault();
        const destination = link.getAttribute('href');
        enqueue(async () => {
          const response = await fetch('/__pyreact/render?path=' + encodeURIComponent(destination));
          history.pushState({}, '', destination);
          apply(await response.json());
        }).catch(console.error);
        return;
      }
      const node = event.target.closest?.('[data-pyreact-events]');
      if (!node || !node.dataset.pyreactEvents.split(',').includes(type)) return;
      if (type === 'submit') event.preventDefault();
      sendEvent(node, type, event).catch(console.error);
    }, true);
  }
  addEventListener('popstate', () => {
    const destination = location.pathname + location.search;
    enqueue(async () => {
      const response = await fetch('/__pyreact/render?path=' + encodeURIComponent(destination));
      apply(await response.json());
    }).catch(console.error);
  });
  setInterval(async () => {
    const response = await fetch('/__pyreact/version', {cache: 'no-store'});
    const payload = await response.json();
    if (payload.version !== version) location.reload();
  }, 750);
})();'''


def _document_html(content: str, version: int, title: str = 'PyReact App') -> str:
    from ..styles.css_module import get_all_global_css, get_all_module_css
    from ..styles.styled import get_all_styles

    css = '\n'.join(filter(None, [get_all_styles(), get_all_global_css(), get_all_module_css()]))
    style_tag = f'<style data-pyreact-styles>{css}</style>' if css else ''
    return ('<!doctype html><html lang="en" data-pyreact-version="' + str(version) + '"><head>'
            '<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">'
            f'<title>{escape(title)}</title>{style_tag}</head><body><div id="root">{content}</div>'
            '<script src="/__pyreact/runtime.js" defer></script></body></html>')


def make_handler(application: LiveApplication, title: str = 'PyReact App') -> type[BaseHTTPRequestHandler]:
    class Handler(BaseHTTPRequestHandler):
        def _session_id(self) -> Optional[str]:
            cookie = self.headers.get('Cookie', '')
            for part in cookie.split(';'):
                name, _, value = part.strip().partition('=')
                if name == 'pyreact_session':
                    return value
            return None

        def _send(self, body: bytes, content_type: str, status: int = 200,
                  session_id: Optional[str] = None) -> None:
            self.send_response(status)
            self.send_header('Content-Type', content_type)
            self.send_header('Content-Length', str(len(body)))
            self.send_header('Cache-Control', 'no-store')
            if session_id:
                self.send_header('Set-Cookie',
                                 f'pyreact_session={session_id}; Path=/; HttpOnly; SameSite=Lax')
            self.end_headers()
            self.wfile.write(body)

        def _json(self, value: Any, status: int = 200,
                  session_id: Optional[str] = None) -> None:
            self._send(json.dumps(value).encode(), 'application/json; charset=utf-8', status, session_id)

        def do_GET(self) -> None:
            application.reload_if_changed()
            parsed = urlsplit(self.path)
            if parsed.path == '/__pyreact/runtime.js':
                self._send(_BROWSER_RUNTIME.encode(), 'text/javascript; charset=utf-8')
                return
            if parsed.path == '/__pyreact/version':
                self._json({'version': application.version})
                return
            static_file = (application.public_dir / parsed.path.lstrip('/')).resolve()
            try:
                static_file.relative_to(application.public_dir)
            except ValueError:
                static_file = application.public_dir / '__invalid__'
            if static_file.is_file() and static_file.name != 'index.html':
                content_type = mimetypes.guess_type(static_file.name)[0] or 'application/octet-stream'
                self._send(static_file.read_bytes(), content_type)
                return
            session_id, session = application.session(self._session_id())
            if parsed.path == '/__pyreact/render':
                target = parse_qs(parsed.query).get('path', ['/'])[0]
                self._json({'html': session.render_path(target), 'version': application.version},
                           session_id=session_id)
                return
            requested = parsed.path + (('?' + parsed.query) if parsed.query else '')
            content = session.render_path(requested)
            page = _document_html(content, application.version, title)
            self._send(page.encode(), 'text/html; charset=utf-8', session_id=session_id)

        def do_POST(self) -> None:
            if urlsplit(self.path).path != '/__pyreact/event':
                self._json({'error': 'Not found'}, HTTPStatus.NOT_FOUND)
                return
            session_id, session = application.session(self._session_id())
            try:
                length = int(self.headers.get('Content-Length', '0'))
                data = json.loads(self.rfile.read(length) or b'{}')
                html = session.dispatch(str(data['path']), str(data['type']), data.get('payload', {}))
                self._json({'html': html, 'version': application.version}, session_id=session_id)
            except (KeyError, ValueError, LookupError, json.JSONDecodeError) as error:
                self._json({'error': str(error)}, HTTPStatus.BAD_REQUEST, session_id)

        def log_message(self, format: str, *args: Any) -> None:
            return None

    return Handler


def serve(entry: str = 'src/index.py', host: str = '127.0.0.1', port: int = 3000,
          public_dir: str = 'public', title: str = 'PyReact App') -> None:
    application = LiveApplication(Path(entry), Path(public_dir))
    server = ThreadingHTTPServer((host, port), make_handler(application, title))
    print(f'[OK] PyReact live server running at http://{host}:{port}', flush=True)
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()