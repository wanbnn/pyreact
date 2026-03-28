"""
PyReact Core Module
===================

This module contains the core functionality of PyReact framework:
- VNode: Virtual DOM node representation
- Component: Base class for stateful components
- h(): Hyperscript function for creating elements
- Reconciler: Diff algorithm for efficient updates
- Renderer: DOM rendering engine
"""

from .element import VNode, h, create_element
from .component import Component
from .renderer import render, hydrate, create_root
from .reconciler import Reconciler
from .hooks import (
    use_state,
    use_reducer,
    use_effect,
    use_layout_effect,
    use_context,
    use_ref,
    use_memo,
    use_callback,
    use_imperative_handle,
    use_debug_value,
    use_id,
    use_transition,
    use_deferred_value,
)
from .context import create_context
from .refs import create_ref, forward_ref
from .portal import create_portal
from .memo import memo, lazy
from .error_boundary import ErrorBoundary
from .scheduler import Scheduler

__all__ = [
    # Element
    'VNode',
    'h',
    'create_element',
    # Component
    'Component',
    # Renderer
    'render',
    'hydrate',
    'create_root',
    # Reconciler
    'Reconciler',
    # Hooks
    'use_state',
    'use_reducer',
    'use_effect',
    'use_layout_effect',
    'use_context',
    'use_ref',
    'use_memo',
    'use_callback',
    'use_imperative_handle',
    'use_debug_value',
    'use_id',
    'use_transition',
    'use_deferred_value',
    # Context
    'create_context',
    # Refs
    'create_ref',
    'forward_ref',
    # Portal
    'create_portal',
    # Memo
    'memo',
    'lazy',
    # Error Boundary
    'ErrorBoundary',
    # Scheduler
    'Scheduler',
]
