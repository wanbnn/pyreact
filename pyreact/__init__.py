"""
PyReact - Framework Web Declarativo para Python
================================================

PyReact é um framework web declarativo inspirado no React, mas construído
nativamente para Python. Permite criar interfaces de usuário reativas,
componentizadas e modernas, sem precisar aprender JavaScript/TypeScript.

Quick Start:
    from pyreact import h, render, use_state
    
    def Counter(props):
        count, set_count = use_state(0)
        return h('div', {'className': 'counter'},
            h('span', None, f"Count: {count}"),
            h('button', {'onClick': lambda _: set_count(count + 1)}, '+')
        )
    
    render(h(Counter, None), document.getElementById('root'))

Princípios:
    - Declaratividade: A UI é uma função do estado
    - Componentização: Tudo é um componente
    - Reatividade: Mudanças de estado disparam re-renderizações
    - Isomorfismo: Suporte a Server-Side Rendering
"""

__version__ = '1.0.0'
__author__ = 'PyReact Team'

# Core
from .core.element import VNode, h, create_element, is_valid_element, clone_element
from .core.component import Component, PureComponent
from .core.renderer import render, hydrate, create_root
from .core.reconciler import Reconciler

# Hooks
from .core.hooks import (
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

# Context
from .core.context import create_context

# Refs
from .core.refs import create_ref, forward_ref

# Portal
from .core.portal import create_portal

# Memo
from .core.memo import memo, lazy

# Error Boundary
from .core.error_boundary import ErrorBoundary

# Scheduler
from .core.scheduler import Scheduler, Priority

# Styles
from .styles import styled, css_module

# Server
from .server.ssr import render_to_string, render_to_static_markup

# DOM
from .dom.dom_operations import document

__all__ = [
    # Version
    '__version__',
    
    # Core
    'VNode',
    'h',
    'create_element',
    'is_valid_element',
    'clone_element',
    'Component',
    'PureComponent',
    'render',
    'hydrate',
    'create_root',
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
    'Priority',
    
    # Styles
    'styled',
    'css_module',
    
    # Server
    'render_to_string',
    'render_to_static_markup',
    
    # DOM
    'document',
]
