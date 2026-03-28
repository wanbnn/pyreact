"""
Synthetic Events Module
=======================

This module implements synthetic events for cross-browser compatibility.
Synthetic events normalize browser differences and provide a consistent API.
"""

from typing import Any, Callable, Dict, Optional
from enum import Enum


class EventType(Enum):
    """Event type categories"""
    CLIPBOARD = 'clipboard'
    KEYBOARD = 'keyboard'
    FOCUS = 'focus'
    FORM = 'form'
    MOUSE = 'mouse'
    TOUCH = 'touch'
    UI = 'ui'
    DRAG = 'drag'
    ANIMATION = 'animation'
    TRANSITION = 'transition'


# Supported event types
EVENT_TYPES = {
    # Clipboard
    'onCopy', 'onCut', 'onPaste',
    # Keyboard
    'onKeyDown', 'onKeyPress', 'onKeyUp',
    # Focus
    'onFocus', 'onBlur',
    # Form
    'onChange', 'onInput', 'onSubmit', 'onReset',
    # Mouse
    'onClick', 'onDoubleClick', 'onMouseDown', 'onMouseUp',
    'onMouseEnter', 'onMouseLeave', 'onMouseMove', 'onMouseOut', 'onMouseOver',
    # Touch
    'onTouchStart', 'onTouchMove', 'onTouchEnd', 'onTouchCancel',
    # UI
    'onScroll', 'onResize',
    # Drag
    'onDrag', 'onDragEnd', 'onDragEnter', 'onDragExit',
    'onDragLeave', 'onDragOver', 'onDragStart', 'onDrop',
    # Animation
    'onAnimationStart', 'onAnimationEnd', 'onAnimationIteration',
    # Transition
    'onTransitionEnd',
}


class SyntheticEvent:
    """
    Base synthetic event class
    
    Provides a cross-browser compatible event object.
    
    Attributes:
        type: Event type (e.g., 'click', 'change')
        target: Element that dispatched the event
        currentTarget: Current element in the bubbling phase
        nativeEvent: Native browser event
        bubbles: Whether the event bubbles
        cancelable: Whether the event can be canceled
        timeStamp: Time when event was created
    """
    
    def __init__(self, native_event: Optional[Dict] = None):
        self.native_event = native_event or {}
        self.type = self.native_event.get('type', '')
        self.target = self.native_event.get('target')
        self.current_target = self.native_event.get('currentTarget')
        self.bubbles = self.native_event.get('bubbles', True)
        self.cancelable = self.native_event.get('cancelable', True)
        self.time_stamp = self.native_event.get('timeStamp', 0)
        
        self._propagation_stopped = False
        self._default_prevented = False
        self._is_persisted = False
    
    def stop_propagation(self) -> None:
        """Stop event propagation (bubbling)"""
        self._propagation_stopped = True
        if hasattr(self.native_event, 'stopPropagation'):
            self.native_event.stopPropagation()
    
    def prevent_default(self) -> None:
        """Prevent default browser action"""
        self._default_prevented = True
        if hasattr(self.native_event, 'preventDefault'):
            self.native_event.preventDefault()
    
    def persist(self) -> None:
        """
        Persist the event for asynchronous use
        
        By default, events are pooled and reused. Call persist()
        to keep the event for later use.
        """
        self._is_persisted = True
    
    def is_propagation_stopped(self) -> bool:
        """Check if propagation was stopped"""
        return self._propagation_stopped
    
    def is_default_prevented(self) -> bool:
        """Check if default was prevented"""
        return self._default_prevented
    
    def __repr__(self) -> str:
        return f"SyntheticEvent(type={self.type!r})"


class SyntheticMouseEvent(SyntheticEvent):
    """
    Synthetic mouse event
    
    Additional attributes:
        clientX, clientY: Coordinates relative to viewport
        pageX, pageY: Coordinates relative to document
        screenX, screenY: Coordinates relative to screen
        button: Mouse button pressed
        buttons: Buttons being pressed (bitfield)
        altKey, ctrlKey, metaKey, shiftKey: Modifier keys
    """
    
    def __init__(self, native_event: Optional[Dict] = None):
        super().__init__(native_event)
        self.client_x = self.native_event.get('clientX', 0)
        self.client_y = self.native_event.get('clientY', 0)
        self.page_x = self.native_event.get('pageX', 0)
        self.page_y = self.native_event.get('pageY', 0)
        self.screen_x = self.native_event.get('screenX', 0)
        self.screen_y = self.native_event.get('screenY', 0)
        self.button = self.native_event.get('button', 0)
        self.buttons = self.native_event.get('buttons', 0)
        self.alt_key = self.native_event.get('altKey', False)
        self.ctrl_key = self.native_event.get('ctrlKey', False)
        self.meta_key = self.native_event.get('metaKey', False)
        self.shift_key = self.native_event.get('shiftKey', False)
    
    def get_modifier_state(self, key: str) -> bool:
        """Check if a modifier key is pressed"""
        states = {
            'Alt': self.alt_key,
            'Control': self.ctrl_key,
            'Meta': self.meta_key,
            'Shift': self.shift_key,
        }
        return states.get(key, False)


class SyntheticKeyboardEvent(SyntheticEvent):
    """
    Synthetic keyboard event
    
    Additional attributes:
        key: Key value
        code: Physical key code
        keyCode: Deprecated key code
        charCode: Deprecated char code
        altKey, ctrlKey, metaKey, shiftKey: Modifier keys
        repeat: Whether key is repeating
        location: Key location
    """
    
    def __init__(self, native_event: Optional[Dict] = None):
        super().__init__(native_event)
        self.key = self.native_event.get('key', '')
        self.code = self.native_event.get('code', '')
        self.key_code = self.native_event.get('keyCode', 0)
        self.char_code = self.native_event.get('charCode', 0)
        self.alt_key = self.native_event.get('altKey', False)
        self.ctrl_key = self.native_event.get('ctrlKey', False)
        self.meta_key = self.native_event.get('metaKey', False)
        self.shift_key = self.native_event.get('shiftKey', False)
        self.repeat = self.native_event.get('repeat', False)
        self.location = self.native_event.get('location', 0)
    
    def get_modifier_state(self, key: str) -> bool:
        """Check if a modifier key is pressed"""
        states = {
            'Alt': self.alt_key,
            'Control': self.ctrl_key,
            'Meta': self.meta_key,
            'Shift': self.shift_key,
        }
        return states.get(key, False)


class SyntheticFocusEvent(SyntheticEvent):
    """
    Synthetic focus event
    
    Additional attributes:
        relatedTarget: Element losing/gaining focus
    """
    
    def __init__(self, native_event: Optional[Dict] = None):
        super().__init__(native_event)
        self.related_target = self.native_event.get('relatedTarget')


class SyntheticFormEvent(SyntheticEvent):
    """
    Synthetic form event
    
    For change, input, submit events.
    """
    
    def __init__(self, native_event: Optional[Dict] = None):
        super().__init__(native_event)
        self.value = self.native_event.get('target', {}).get('value', '')
        self.checked = self.native_event.get('target', {}).get('checked', False)


class SyntheticTouchEvent(SyntheticEvent):
    """
    Synthetic touch event
    
    Additional attributes:
        touches: List of touches currently on screen
        targetTouches: List of touches on target element
        changedTouches: List of touches that changed
    """
    
    def __init__(self, native_event: Optional[Dict] = None):
        super().__init__(native_event)
        self.touches = self.native_event.get('touches', [])
        self.target_touches = self.native_event.get('targetTouches', [])
        self.changed_touches = self.native_event.get('changedTouches', [])
        self.alt_key = self.native_event.get('altKey', False)
        self.ctrl_key = self.native_event.get('ctrlKey', False)
        self.meta_key = self.native_event.get('metaKey', False)
        self.shift_key = self.native_event.get('shiftKey', False)


class SyntheticDragEvent(SyntheticMouseEvent):
    """
    Synthetic drag event
    
    Additional attributes:
        dataTransfer: Data transfer object
    """
    
    def __init__(self, native_event: Optional[Dict] = None):
        super().__init__(native_event)
        self.data_transfer = self.native_event.get('dataTransfer')


class SyntheticAnimationEvent(SyntheticEvent):
    """
    Synthetic animation event
    
    Additional attributes:
        animationName: Name of the animation
        elapsedTime: Elapsed time in seconds
        pseudoElement: Pseudo element name
    """
    
    def __init__(self, native_event: Optional[Dict] = None):
        super().__init__(native_event)
        self.animation_name = self.native_event.get('animationName', '')
        self.elapsed_time = self.native_event.get('elapsedTime', 0)
        self.pseudo_element = self.native_event.get('pseudoElement', '')


class SyntheticTransitionEvent(SyntheticEvent):
    """
    Synthetic transition event
    
    Additional attributes:
        propertyName: Name of the CSS property
        elapsedTime: Elapsed time in seconds
        pseudoElement: Pseudo element name
    """
    
    def __init__(self, native_event: Optional[Dict] = None):
        super().__init__(native_event)
        self.property_name = self.native_event.get('propertyName', '')
        self.elapsed_time = self.native_event.get('elapsedTime', 0)
        self.pseudo_element = self.native_event.get('pseudoElement', '')


def create_synthetic_event(event_type: str, native_event: Dict) -> SyntheticEvent:
    """
    Create the appropriate synthetic event type
    
    Args:
        event_type: Event type name
        native_event: Native event object
    
    Returns:
        SyntheticEvent: Appropriate synthetic event subclass
    """
    event_map = {
        'click': SyntheticMouseEvent,
        'dblclick': SyntheticMouseEvent,
        'mousedown': SyntheticMouseEvent,
        'mouseup': SyntheticMouseEvent,
        'mousemove': SyntheticMouseEvent,
        'mouseover': SyntheticMouseEvent,
        'mouseout': SyntheticMouseEvent,
        'mouseenter': SyntheticMouseEvent,
        'mouseleave': SyntheticMouseEvent,
        'keydown': SyntheticKeyboardEvent,
        'keyup': SyntheticKeyboardEvent,
        'keypress': SyntheticKeyboardEvent,
        'focus': SyntheticFocusEvent,
        'blur': SyntheticFocusEvent,
        'change': SyntheticFormEvent,
        'input': SyntheticFormEvent,
        'submit': SyntheticFormEvent,
        'touchstart': SyntheticTouchEvent,
        'touchmove': SyntheticTouchEvent,
        'touchend': SyntheticTouchEvent,
        'touchcancel': SyntheticTouchEvent,
        'drag': SyntheticDragEvent,
        'dragstart': SyntheticDragEvent,
        'dragend': SyntheticDragEvent,
        'dragenter': SyntheticDragEvent,
        'dragleave': SyntheticDragEvent,
        'dragover': SyntheticDragEvent,
        'drop': SyntheticDragEvent,
        'animationstart': SyntheticAnimationEvent,
        'animationend': SyntheticAnimationEvent,
        'animationiteration': SyntheticAnimationEvent,
        'transitionend': SyntheticTransitionEvent,
    }
    
    event_class = event_map.get(event_type.lower(), SyntheticEvent)
    return event_class(native_event)


def get_native_event_type(react_event_type: str) -> str:
    """
    Convert React-style event type to native event type
    
    Args:
        react_event_type: React event type (e.g., 'onClick')
    
    Returns:
        str: Native event type (e.g., 'click')
    """
    if react_event_type.startswith('on'):
        return react_event_type[2:].lower()
    return react_event_type.lower()
