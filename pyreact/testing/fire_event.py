"""
Fire Event Module
=================

Event firing utilities for testing.
"""

from typing import Any, Dict, Optional


class FireEvent:
    """
    Event firing utilities for testing
    
    Provides methods to simulate user interactions.
    
    Example:
        result = render(h(Button, {'onClick': handle_click}, 'Click'))
        button = result.get_by_role('button')
        
        fire_event.click(button)
        fire_event.change(input, {'target': {'value': 'text'}})
    """
    
    @staticmethod
    def click(element: Any, options: Optional[Dict] = None) -> None:
        """
        Fire click event
        
        Args:
            element: Element to click
            options: Event options
        """
        event = {
            'type': 'click',
            'target': element,
            'currentTarget': element,
            'bubbles': True,
            'cancelable': True,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onClick', event)
    
    @staticmethod
    def change(element: Any, options: Optional[Dict] = None) -> None:
        """
        Fire change event
        
        Args:
            element: Element to change
            options: Event options (e.g., {'target': {'value': 'new value'}})
        """
        event = {
            'type': 'change',
            'target': options.get('target', element) if options else element,
            'currentTarget': element,
            'bubbles': True,
            'cancelable': True,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onChange', event)
    
    @staticmethod
    def input(element: Any, options: Optional[Dict] = None) -> None:
        """
        Fire input event
        
        Args:
            element: Element
            options: Event options
        """
        event = {
            'type': 'input',
            'target': options.get('target', element) if options else element,
            'currentTarget': element,
            'bubbles': True,
            'cancelable': True,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onInput', event)
    
    @staticmethod
    def submit(element: Any, options: Optional[Dict] = None) -> None:
        """
        Fire submit event
        
        Args:
            element: Form element
            options: Event options
        """
        event = {
            'type': 'submit',
            'target': element,
            'currentTarget': element,
            'bubbles': True,
            'cancelable': True,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onSubmit', event)
    
    @staticmethod
    def focus(element: Any, options: Optional[Dict] = None) -> None:
        """
        Fire focus event
        
        Args:
            element: Element to focus
            options: Event options
        """
        event = {
            'type': 'focus',
            'target': element,
            'currentTarget': element,
            'bubbles': False,
            'cancelable': False,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onFocus', event)
    
    @staticmethod
    def blur(element: Any, options: Optional[Dict] = None) -> None:
        """
        Fire blur event
        
        Args:
            element: Element to blur
            options: Event options
        """
        event = {
            'type': 'blur',
            'target': element,
            'currentTarget': element,
            'bubbles': False,
            'cancelable': False,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onBlur', event)
    
    @staticmethod
    def key_down(element: Any, key: str, options: Optional[Dict] = None) -> None:
        """
        Fire keydown event
        
        Args:
            element: Element
            key: Key pressed
            options: Event options
        """
        event = {
            'type': 'keydown',
            'key': key,
            'target': element,
            'currentTarget': element,
            'bubbles': True,
            'cancelable': True,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onKeyDown', event)
    
    @staticmethod
    def key_up(element: Any, key: str, options: Optional[Dict] = None) -> None:
        """
        Fire keyup event
        
        Args:
            element: Element
            key: Key released
            options: Event options
        """
        event = {
            'type': 'keyup',
            'key': key,
            'target': element,
            'currentTarget': element,
            'bubbles': True,
            'cancelable': True,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onKeyUp', event)
    
    @staticmethod
    def mouse_enter(element: Any, options: Optional[Dict] = None) -> None:
        """
        Fire mouseenter event
        
        Args:
            element: Element
            options: Event options
        """
        event = {
            'type': 'mouseenter',
            'target': element,
            'currentTarget': element,
            'bubbles': False,
            'cancelable': False,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onMouseEnter', event)
    
    @staticmethod
    def mouse_leave(element: Any, options: Optional[Dict] = None) -> None:
        """
        Fire mouseleave event
        
        Args:
            element: Element
            options: Event options
        """
        event = {
            'type': 'mouseleave',
            'target': element,
            'currentTarget': element,
            'bubbles': False,
            'cancelable': False,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onMouseLeave', event)
    
    @staticmethod
    def mouse_down(element: Any, options: Optional[Dict] = None) -> None:
        """
        Fire mousedown event
        
        Args:
            element: Element
            options: Event options
        """
        event = {
            'type': 'mousedown',
            'target': element,
            'currentTarget': element,
            'bubbles': True,
            'cancelable': True,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onMouseDown', event)
    
    @staticmethod
    def mouse_up(element: Any, options: Optional[Dict] = None) -> None:
        """
        Fire mouseup event
        
        Args:
            element: Element
            options: Event options
        """
        event = {
            'type': 'mouseup',
            'target': element,
            'currentTarget': element,
            'bubbles': True,
            'cancelable': True,
            **(options or {})
        }
        FireEvent._dispatch_event(element, 'onMouseUp', event)
    
    @staticmethod
    def _dispatch_event(element: Any, event_name: str, event_data: Dict) -> None:
        """
        Dispatch an event to an element
        
        Args:
            element: Element
            event_name: Event handler name (e.g., 'onClick')
            event_data: Event data
        """
        # Get event handler
        handler = None
        if hasattr(element, 'props'):
            handler = element.props.get(event_name)
        elif hasattr(element, event_name):
            handler = getattr(element, event_name)
        
        # Call handler
        if handler:
            from .dom.events import create_synthetic_event
            synthetic_event = create_synthetic_event(event_data.get('type', ''), event_data)
            handler(synthetic_event)


# Convenience functions
def fire_event(element: Any, event_name: str, event_data: Optional[Dict] = None) -> None:
    """
    Fire an event on an element
    
    Args:
        element: Element
        event_name: Event name (e.g., 'click', 'change')
        event_data: Event data
    """
    event_map = {
        'click': FireEvent.click,
        'change': FireEvent.change,
        'input': FireEvent.input,
        'submit': FireEvent.submit,
        'focus': FireEvent.focus,
        'blur': FireEvent.blur,
        'keydown': FireEvent.key_down,
        'keyup': FireEvent.key_up,
        'mouseenter': FireEvent.mouse_enter,
        'mouseleave': FireEvent.mouse_leave,
        'mousedown': FireEvent.mouse_down,
        'mouseup': FireEvent.mouse_up,
    }
    
    handler = event_map.get(event_name.lower())
    if handler:
        handler(element, event_data)
    else:
        FireEvent._dispatch_event(element, f'on{event_name.capitalize()}', event_data or {})


def click(element: Any, options: Optional[Dict] = None) -> None:
    """Fire click event"""
    FireEvent.click(element, options)


def change(element: Any, options: Optional[Dict] = None) -> None:
    """Fire change event"""
    FireEvent.change(element, options)


def submit(element: Any, options: Optional[Dict] = None) -> None:
    """Fire submit event"""
    FireEvent.submit(element, options)


def focus(element: Any, options: Optional[Dict] = None) -> None:
    """Fire focus event"""
    FireEvent.focus(element, options)


def blur(element: Any, options: Optional[Dict] = None) -> None:
    """Fire blur event"""
    FireEvent.blur(element, options)


def key_down(element: Any, key: str, options: Optional[Dict] = None) -> None:
    """Fire keydown event"""
    FireEvent.key_down(element, key, options)


def key_up(element: Any, key: str, options: Optional[Dict] = None) -> None:
    """Fire keyup event"""
    FireEvent.key_up(element, key, options)


def mouse_enter(element: Any, options: Optional[Dict] = None) -> None:
    """Fire mouseenter event"""
    FireEvent.mouse_enter(element, options)


def mouse_leave(element: Any, options: Optional[Dict] = None) -> None:
    """Fire mouseleave event"""
    FireEvent.mouse_leave(element, options)
