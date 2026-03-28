"""
PyReact Server Module
=====================

This module provides server-side rendering (SSR) functionality:
- render_to_string: Render component to HTML string
- render_to_static_markup: Render without data attributes
- hydration: Client-side hydration for interactivity
"""

from .ssr import (
    render_to_string,
    render_to_static_markup,
    render_to_node_stream,
    render_to_static_node_stream,
)

from .hydration import (
    hydrate,
    hydrate_root,
    HydrationMismatchError,
)

__all__ = [
    # SSR
    'render_to_string',
    'render_to_static_markup',
    'render_to_node_stream',
    'render_to_static_node_stream',
    # Hydration
    'hydrate',
    'hydrate_root',
    'HydrationMismatchError',
]
