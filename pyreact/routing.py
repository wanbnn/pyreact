"""Small, dependency-free router for server-driven PyReact applications."""

from contextlib import contextmanager
from contextvars import ContextVar
from dataclasses import dataclass
import re
from typing import Any, Callable, Dict, Iterable, Iterator, Optional, Tuple
from urllib.parse import parse_qs, urlsplit

from .core.element import VNode, h


@dataclass(frozen=True)
class Location:
    pathname: str = '/'
    search: str = ''
    query: Dict[str, list[str]] = None  # type: ignore[assignment]

    def __post_init__(self) -> None:
        object.__setattr__(self, 'query', self.query or {})


@dataclass(frozen=True)
class Route:
    path: str
    component: Callable[[Dict[str, Any]], VNode]
    exact: bool = True


_location: ContextVar[Location] = ContextVar('pyreact_location', default=Location())
_params: ContextVar[Dict[str, str]] = ContextVar('pyreact_route_params', default={})


def route(path: str, component: Callable[[Dict[str, Any]], VNode], exact: bool = True) -> Route:
    return Route(path, component, exact)


def _compile_path(pattern: str, exact: bool) -> re.Pattern[str]:
    if pattern == '*':
        return re.compile(r'^.*$')
    parts = []
    for part in pattern.strip('/').split('/') if pattern != '/' else []:
        if part.startswith(':'):
            name = part[1:]
            if not name.isidentifier():
                raise ValueError(f'Invalid route parameter: {name!r}')
            parts.append(fr'(?P<{name}>[^/]+)')
        elif part == '*':
            parts.append(r'(?P<wildcard>.*)')
        else:
            parts.append(re.escape(part))
    expression = '/' + '/'.join(parts)
    if pattern == '/':
        expression = '/'
    return re.compile('^' + expression + ('$' if exact else r'(?:/|$)'))


def match_path(pattern: str, pathname: str, exact: bool = True) -> Optional[Dict[str, str]]:
    match = _compile_path(pattern, exact).match(pathname or '/')
    return match.groupdict() if match else None


def _parse_location(url: str) -> Location:
    parsed = urlsplit(url)
    return Location(parsed.path or '/', parsed.query, parse_qs(parsed.query))


def set_location(url: str) -> Location:
    location = _parse_location(url)
    _location.set(location)
    return location


@contextmanager
def routing_context(url: str) -> Iterator[Location]:
    location_token = _location.set(_parse_location(url))
    params_token = _params.set({})
    try:
        yield _location.get()
    finally:
        _params.reset(params_token)
        _location.reset(location_token)


def Router(props: Dict[str, Any]) -> VNode:
    routes: Iterable[Route] = props.get('routes', [])
    configured_location = props.get('location')
    if isinstance(configured_location, str):
        location = _parse_location(configured_location)
    elif isinstance(configured_location, Location):
        location = configured_location
    else:
        location = _location.get()
    for candidate in routes:
        params = match_path(candidate.path, location.pathname, candidate.exact)
        if params is not None:
            _params.set(params)
            return h(candidate.component, {
                'params': params,
                'location': location,
            })
    fallback = props.get('fallback')
    if isinstance(fallback, VNode):
        return fallback
    if callable(fallback):
        return h(fallback, {'location': location})
    return h('h1', {'role': 'alert'}, '404 — Not Found')


def Link(props: Dict[str, Any]) -> VNode:
    destination = props.get('to', '/')
    children = props.get('children', [])
    anchor_props = {key: value for key, value in props.items() if key not in ('to', 'children')}
    anchor_props.update({'href': destination, 'data-pyreact-link': 'true'})
    return h('a', anchor_props, children)


def Navigate(props: Dict[str, Any]) -> VNode:
    destination = props.get('to', '/')
    return h('meta', {'http-equiv': 'refresh', 'content': f'0;url={destination}'})


def use_location() -> Location:
    return _location.get()


def use_params() -> Dict[str, str]:
    return _params.get().copy()
