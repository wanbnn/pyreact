"""
Refs Module
===========

This module implements the Ref system for accessing DOM nodes
and component instances directly.
"""

from typing import Any, Callable, Dict, Optional, TYPE_CHECKING

if TYPE_CHECKING:
    from .element import VNode


class Ref:
    """
    Reference to a DOM node or component instance
    
    Refs provide a way to access DOM nodes or component instances
    directly without using props.
    
    Example:
        class TextInput(Component):
            def __init__(self, props):
                super().__init__(props)
                self.input_ref = create_ref()
            
            def focus(self):
                self.input_ref.current.focus()
            
            def render(self):
                return h('input', {'ref': self.input_ref, 'type': 'text'})
    """
    
    def __init__(self):
        self.current: Any = None
    
    def __repr__(self) -> str:
        return f"Ref(current={self.current!r})"


def create_ref() -> Ref:
    """
    Create a new Ref object
    
    Returns:
        Ref: A new reference object
    
    Example:
        input_ref = create_ref()
        h('input', {'ref': input_ref})
    """
    return Ref()


def forward_ref(render: Callable) -> Callable:
    """
    Forward a ref through a component to a DOM element
    
    Allows a component to forward a ref to one of its children.
    
    Args:
        render: Function (props, ref) -> VNode
    
    Returns:
        Component that forwards the ref
    
    Example:
        @forward_ref
        def FancyInput(props, ref):
            return h('input', {
                'ref': ref,
                'className': 'fancy-input',
                **props
            })
        
        # Usage
        input_ref = create_ref()
        h(FancyInput, {'ref': input_ref, 'placeholder': 'Type here'})
    """
    def wrapper(props: Dict[str, Any]) -> 'VNode':
        ref = props.pop('ref', None)
        return render(props, ref)
    
    wrapper._forward_ref = True
    wrapper.__name__ = render.__name__
    wrapper.__doc__ = render.__doc__
    
    return wrapper


def use_imperative_handle(
    ref: Optional[Ref],
    create_handle: Callable[[], Any],
    dependencies: Optional[list] = None
) -> None:
    """
    Customize the instance value exposed to parent components
    
    Use with forward_ref to expose specific methods to the parent.
    
    Args:
        ref: Ref passed from parent
        create_handle: Function that returns object to expose
        dependencies: List of values that trigger handle update
    
    Example:
        @forward_ref
        def FancyInput(props, ref):
            input_ref = use_ref(None)
            
            use_imperative_handle(ref, lambda: {
                'focus': lambda: input_ref.current.focus(),
                'scrollIntoView': lambda: input_ref.current.scrollIntoView()
            }, [])
            
            return h('input', {'ref': input_ref, **props})
    """
    from .hooks import use_effect
    
    def effect():
        if ref:
            ref.current = create_handle()
        return lambda: None
    
    use_effect(effect, dependencies)


class CallbackRef:
    """
    Callback-based ref
    
    Called with the DOM node when it's mounted or unmounted.
    
    Example:
        def set_input_ref(node):
            if node:
                node.focus()
        
        h('input', {'ref': set_input_ref})
    """
    
    def __init__(self, callback: Callable[[Optional[Any]], None]):
        self.callback = callback
        self.current: Optional[Any] = None
    
    def __call__(self, node: Optional[Any]) -> None:
        """Called when ref is set"""
        self.current = node
        self.callback(node)


def create_callback_ref(callback: Callable[[Optional[Any]], None]) -> CallbackRef:
    """
    Create a callback ref
    
    Args:
        callback: Function called with the DOM node
    
    Returns:
        CallbackRef: A callback-based reference
    
    Example:
        def on_input_mount(node):
            if node:
                node.focus()
        
        ref = create_callback_ref(on_input_mount)
        h('input', {'ref': ref})
    """
    return CallbackRef(callback)


def is_ref(value: Any) -> bool:
    """
    Check if a value is a valid ref
    
    Args:
        value: Value to check
    
    Returns:
        bool: True if value is a ref
    """
    return isinstance(value, (Ref, CallbackRef)) or callable(value)


def attach_ref(ref: Any, value: Any) -> None:
    """
    Attach a value to a ref
    
    Args:
        ref: Ref object or callback
        value: Value to attach
    """
    if ref is None:
        return
    
    if isinstance(ref, Ref):
        ref.current = value
    elif callable(ref):
        ref(value)
    elif isinstance(ref, CallbackRef):
        ref(value)


def detach_ref(ref: Any) -> None:
    """
    Detach a value from a ref
    
    Args:
        ref: Ref object or callback
    """
    attach_ref(ref, None)
