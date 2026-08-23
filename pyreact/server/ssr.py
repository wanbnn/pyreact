"""
Server-Side Rendering Module
============================

This module implements server-side rendering for PyReact components.
"""

from contextvars import ContextVar
from typing import Any, AsyncIterator, Dict, Iterator, List, Optional, Union
from ..core.element import VNode
from ..core.component import Component


# Void elements (self-closing)
VOID_ELEMENTS = {
    'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input',
    'link', 'meta', 'param', 'source', 'track', 'wbr',
}

# Elements that don't need closing tag
HTML_ELEMENTS = {
    'html', 'head', 'body', 'div', 'span', 'p', 'a', 'img',
    'ul', 'ol', 'li', 'table', 'tr', 'td', 'th', 'form',
    'input', 'button', 'select', 'option', 'textarea', 'label',
    'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'header', 'footer',
    'nav', 'main', 'section', 'article', 'aside', 'script', 'style',
}
_ssr_component_counter: ContextVar[int] = ContextVar('pyreact_ssr_component_counter', default=0)


def render_to_string(element: Union[VNode, str, None]) -> str:
    """
    Render an element to an HTML string
    
    Includes data attributes for client-side hydration.
    
    Args:
        element: VNode or string to render
    
    Returns:
        str: HTML string
    
    Example:
        html = render_to_string(h(App, None))
        # Returns: '<div data-reactroot="">...</div>'
    """
    if element is None:
        return ''
    
    if isinstance(element, str):
        return escape_html(element)
    
    token = _ssr_component_counter.set(0)
    try:
        return _render_node(element, include_data_attrs=True)
    finally:
        _ssr_component_counter.reset(token)


def render_to_static_markup(element: Union[VNode, str, None]) -> str:
    """
    Render an element to HTML without data attributes
    
    Use for static pages, emails, etc.
    
    Args:
        element: VNode or string to render
    
    Returns:
        str: HTML string without data attributes
    
    Example:
        html = render_to_static_markup(h(App, None))
        # Returns: '<div>...</div>'
    """
    if element is None:
        return ''
    
    if isinstance(element, str):
        return escape_html(element)
    
    token = _ssr_component_counter.set(0)
    try:
        return _render_node(element, include_data_attrs=False)
    finally:
        _ssr_component_counter.reset(token)


def _render_node(node: Union[VNode, str], include_data_attrs: bool = True) -> str:
    """
    Render a single VNode to HTML
    
    Args:
        node: VNode to render
        include_data_attrs: Whether to include data attributes
    
    Returns:
        str: HTML string
    """
    if node is None:
        return ''
    
    if isinstance(node, str):
        return escape_html(node)
    
    # Component
    if callable(node.type) and not isinstance(node.type, str):
        return _render_component(node, include_data_attrs)
    
    # HTML element
    tag = node.type
    attrs = _render_attrs(node.props, include_data_attrs)
    # Hydration needs a marker on the rendered root, not on every descendant.
    raw_html = node.props.get('dangerouslySetInnerHTML')
    if raw_html is not None:
        if not isinstance(raw_html, dict) or '__html' not in raw_html:
            raise ValueError('dangerouslySetInnerHTML requires a {"__html": value} mapping')
        children = str(raw_html['__html'])
    else:
        children = ''.join(_render_node(child, False) for child in node.children)
    
    if tag in VOID_ELEMENTS:
        return f'<{tag}{attrs} />'
    else:
        return f'<{tag}{attrs}>{children}</{tag}>'


def _render_component(vnode: VNode, include_data_attrs: bool) -> str:
    """
    Render a component to HTML
    
    Args:
        vnode: Component VNode
        include_data_attrs: Whether to include data attributes
    
    Returns:
        str: HTML string
    """
    from ..core.hooks import _reset_hook_index, _set_current_component

    component_type = vnode.type
    if isinstance(component_type, type):
        component = component_type(vnode.props)
    else:
        component = _SSRFunctionComponent(component_type, vnode.props)
    component._hooks = []
    component._hook_index = 0
    component._tree_id = _ssr_component_counter.get()
    _ssr_component_counter.set(component._tree_id + 1)
    component._is_rendering = True

    provider_context = getattr(component_type, '_pyreact_context_provider', None)
    provider_id = id(component)
    if provider_context is not None:
        provider_context._push_provider(
            provider_id, vnode.props.get('value', provider_context._default_value)
        )

    _set_current_component(component)
    _reset_hook_index()
    try:
        rendered = component.render()
    finally:
        component._is_rendering = False
        _set_current_component(None)

    if isinstance(rendered, list):
        if len(rendered) == 1:
            rendered = rendered[0]
        elif not rendered:
            rendered = None
        else:
            if provider_context is not None:
                provider_context._pop_provider(provider_id)
            raise TypeError('Components must return one VNode during SSR')

    try:
        if rendered is None:
            return ''
        try:
            return _render_node(rendered, include_data_attrs)
        except Exception as error:
            derived = component.get_derived_state_from_error(error) if hasattr(
                component, 'get_derived_state_from_error'
            ) else None
            if derived is None:
                raise
            component.state = {**component.state, **derived}
            if hasattr(component, 'component_did_catch'):
                component.component_did_catch(error, {'componentStack': repr(rendered)})
            _set_current_component(component)
            _reset_hook_index()
            try:
                fallback = component.render()
            finally:
                _set_current_component(None)
            return '' if fallback is None else _render_node(fallback, include_data_attrs)
    finally:
        if provider_context is not None:
            provider_context._pop_provider(provider_id)


def _render_attrs(props: Dict[str, Any], include_data_attrs: bool) -> str:
    """
    Render props as HTML attributes
    
    Args:
        props: Props dictionary
        include_data_attrs: Whether to include data attributes
    
    Returns:
        str: HTML attribute string
    """
    result = []
    
    for name, value in props.items():
        # Skip event handlers
        if name.startswith('on'):
            continue
        
        # Skip ref and key
        if name in ('ref', 'key'):
            continue
        
        # Skip style (handled separately)
        if name == 'style':
            style_str = _render_style(value)
            if style_str:
                result.append(f'style="{escape_html(style_str)}"')
            continue
        
        # Skip dangerouslySetInnerHTML
        if name == 'dangerouslySetInnerHTML':
            continue
        
        # Skip children
        if name == 'children':
            continue
        
        # Handle className
        if name == 'className':
            result.append(f'class="{escape_html(value)}"')
            continue
        
        # Handle htmlFor
        if name == 'htmlFor':
            result.append(f'for="{escape_html(value)}"')
            continue
        
        # Boolean attributes
        if value is True:
            result.append(name.lower())
        elif value is not None and value is not False:
            result.append(f'{name.lower()}="{escape_html(str(value))}"')
    
    # Add data-reactroot for hydration
    if include_data_attrs:
        result.append('data-reactroot=""')
    
    if result:
        return ' ' + ' '.join(result)
    return ''


def _render_style(style: Union[str, Dict[str, Any]]) -> str:
    """
    Render style to CSS string
    
    Args:
        style: Style dictionary or string
    
    Returns:
        str: CSS string
    """
    if isinstance(style, str):
        return style
    
    if isinstance(style, dict):
        result = []
        for name, value in style.items():
            # Convert camelCase to kebab-case
            css_name = _camel_to_kebab(name)
            if value is not None:
                result.append(f'{css_name}:{value}')
        return ';'.join(result)
    
    return ''


def _camel_to_kebab(name: str) -> str:
    """
    Convert camelCase to kebab-case
    
    Args:
        name: camelCase string
    
    Returns:
        str: kebab-case string
    """
    result = []
    for char in name:
        if char.isupper():
            result.append('-')
            result.append(char.lower())
        else:
            result.append(char)
    return ''.join(result)


def escape_html(text: str) -> str:
    """
    Escape HTML special characters
    
    Args:
        text: Text to escape
    
    Returns:
        str: Escaped text
    """
    return (
        str(text)
        .replace('&', '&amp;')
        .replace('<', '&lt;')
        .replace('>', '&gt;')
        .replace('"', '&quot;')
        .replace("'", '&#x27;')
    )


def _stream_node(node: Union[VNode, str, None], include_data_attrs: bool = True) -> Iterator[str]:
    """Yield HTML chunks while preserving component and escaping semantics."""
    if node is None:
        return
    if isinstance(node, str) or callable(node.type):
        yield _render_node(node, include_data_attrs)
        return
    attrs = _render_attrs(node.props, include_data_attrs)
    yield f'<{node.type}{attrs}'
    if node.type in VOID_ELEMENTS:
        yield ' />'
        return
    yield '>'
    raw_html = node.props.get('dangerouslySetInnerHTML')
    if raw_html is not None:
        if not isinstance(raw_html, dict) or '__html' not in raw_html:
            raise ValueError('dangerouslySetInnerHTML requires a {"__html": value} mapping')
        yield str(raw_html['__html'])
    else:
        for child in node.children:
            yield from _stream_node(child, False)
    yield f'</{node.type}>'


def render_to_node_stream(element: VNode) -> Iterator[str]:
    """
    Render element to a stream (simplified version)
    
    In a real implementation, this would return an async generator.
    
    Args:
        element: VNode to render
    
    Returns:
        str: HTML string (simplified)
    """
    return _stream_node(element, True)


def render_to_static_node_stream(element: VNode) -> Iterator[str]:
    """
    Render element to a static stream (simplified version)
    
    In a real implementation, this would return an async generator.
    
    Args:
        element: VNode to render
    
    Returns:
        str: HTML string (simplified)
    """
    return _stream_node(element, False)


async def render_to_async_stream(element: VNode, static: bool = False) -> AsyncIterator[str]:
    """Asynchronously yield SSR chunks for ASGI and other async servers."""
    for chunk in _stream_node(element, not static):
        yield chunk


class _SSRFunctionComponent:
    def __init__(self, render_fn: Any, props: Dict[str, Any]):
        self.render_fn = render_fn
        self.props = props
        self.state: Dict[str, Any] = {}
        self._hooks: List[Dict[str, Any]] = []
        self._hook_index = 0
        self._is_rendering = False

    def render(self) -> Any:
        return self.render_fn(self.props)

    def _schedule_update(self) -> None:
        # State updates during SSR are intentionally not committed recursively.
        return None


class SSRContext:
    """
    Context for server-side rendering
    
    Manages context providers and other SSR-specific state.
    """
    
    def __init__(self):
        self.context_providers: List[Any] = []
        self.render_id: str = ''
    
    def push_provider(self, provider: Any) -> None:
        """Push a context provider"""
        self.context_providers.append(provider)
    
    def pop_provider(self) -> Optional[Any]:
        """Pop a context provider"""
        if self.context_providers:
            return self.context_providers.pop()
        return None
    
    def get_context_value(self, context: Any) -> Any:
        """Get current context value"""
        for provider in reversed(self.context_providers):
            if provider.context == context:
                return provider.value
        return context._default_value


def render_to_string_with_context(
    element: VNode,
    context: Optional[SSRContext] = None
) -> str:
    """
    Render with SSR context
    
    Args:
        element: VNode to render
        context: SSR context
    
    Returns:
        str: HTML string
    """
    ctx = context or SSRContext()
    # In a real implementation, this would use the context
    return render_to_string(element)
