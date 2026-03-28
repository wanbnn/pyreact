"""
PyReact DOM Module
==================

This module provides DOM-specific functionality:
- DOM operations (create, update, remove elements)
- Synthetic events (cross-browser event handling)
- Attribute mapping (HTML attributes vs DOM properties)
"""

from .dom_operations import (
    create_element,
    create_text_node,
    append_child,
    remove_child,
    insert_before,
    set_attribute,
    remove_attribute,
    set_style,
    add_event_listener,
    remove_event_listener,
)

from .events import (
    SyntheticEvent,
    SyntheticMouseEvent,
    SyntheticKeyboardEvent,
    SyntheticFocusEvent,
    SyntheticFormEvent,
    EVENT_TYPES,
)

from .attributes import (
    is_custom_attribute,
    should_set_attribute,
    get_attribute_name,
    PROPERTY_NAMES,
)

__all__ = [
    # DOM Operations
    'create_element',
    'create_text_node',
    'append_child',
    'remove_child',
    'insert_before',
    'set_attribute',
    'remove_attribute',
    'set_style',
    'add_event_listener',
    'remove_event_listener',
    # Events
    'SyntheticEvent',
    'SyntheticMouseEvent',
    'SyntheticKeyboardEvent',
    'SyntheticFocusEvent',
    'SyntheticFormEvent',
    'EVENT_TYPES',
    # Attributes
    'is_custom_attribute',
    'should_set_attribute',
    'get_attribute_name',
    'PROPERTY_NAMES',
]
