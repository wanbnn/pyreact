"""
PyReact Testing Module
======================

Testing utilities for PyReact components.
"""

from .test_renderer import (
    render,
    cleanup,
    act,
    RenderResult,
)

from .screen import (
    screen,
    get_by_text,
    get_by_role,
    get_by_test_id,
    query_by_text,
    query_by_role,
    query_by_test_id,
    find_by_text,
    find_by_role,
    find_by_test_id,
)

from .fire_event import (
    FireEvent,
    fire_event,
    click,
    change,
    submit,
    focus,
    blur,
    key_down,
    key_up,
    mouse_enter,
    mouse_leave,
)

__all__ = [
    # Test Renderer
    'render',
    'cleanup',
    'act',
    'RenderResult',
    # Screen
    'screen',
    'get_by_text',
    'get_by_role',
    'get_by_test_id',
    'query_by_text',
    'query_by_role',
    'query_by_test_id',
    'find_by_text',
    'find_by_role',
    'find_by_test_id',
    # FireEvent
    'FireEvent',
    'fire_event',
    'click',
    'change',
    'submit',
    'focus',
    'blur',
    'key_down',
    'key_up',
    'mouse_enter',
    'mouse_leave',
]
