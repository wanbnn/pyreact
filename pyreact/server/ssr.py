"""
Server-Side Rendering Module
============================

This module implements server-side rendering for PyReact components.
"""

from typing import Any, Dict, List, Optional, Union
from .element import VNode
from .component import Component


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
    
    return _render_node(element, include_data_attrs=True)


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
    
    return _render_node(element, include_data_attrs=False)


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
    children = ''.join(_render_node(child, include_data_attrs) for child in node.children)
    
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
    component_type = vnode.type
    
    # Instantiate component
    if isinstance(component_type, type):
        # Class component
        component = component_type(vnode.props)
        rendered = component.render()
    else:
        # Function component
        rendered = component_type(vnode.props)
    
    if rendered is None:
        return ''
    
    return _render_node(rendered, include_data_attrs)


def _render_attrs(props: Dict[str, Any], include_data_attrs: bool) -> str:
    """
    Render props as HTML attributes
    
    Args:
        props: Props dictionary
        include_data_attrs: Whether to include data attributes
    
    Returns:
        str: HTML attribute string
    """
    if not props:
        return ''
    
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
                result.append(f'style="{style_str}"')
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


def render_to_node_stream(element: VNode) -> str:
    """
    Render element to a stream (simplified version)
    
    In a real implementation, this would return an async generator.
    
    Args:
        element: VNode to render
    
    Returns:
        str: HTML string (simplified)
    """
    return render_to_string(element)


def render_to_static_node_stream(element: VNode) -> str:
    """
    Render element to a static stream (simplified version)
    
    In a real implementation, this would return an async generator.
    
    Args:
        element: VNode to render
    
    Returns:
        str: HTML string (simplified)
    """
    return render_to_static_markup(element)


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
