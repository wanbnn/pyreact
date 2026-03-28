"""
Hooks Module
============

This module implements React-style hooks for functional components.
Hooks allow you to use state and other React features without writing a class.
"""

from typing import Any, Callable, Dict, List, Optional, Tuple, Union
from functools import wraps
import uuid

# Global context for hooks
_current_component: Optional[Any] = None
_hook_index: int = 0


def _get_current_component() -> Any:
    """Get the current component context"""
    global _current_component
    if _current_component is None:
        raise RuntimeError('Hooks can only be called inside a component')
    return _current_component


def _set_current_component(component: Any) -> None:
    """Set the current component context"""
    global _current_component, _hook_index
    _current_component = component
    _hook_index = 0


def _reset_hook_index() -> None:
    """Reset hook index for new render"""
    global _hook_index
    _hook_index = 0


def use_state(
    initial_value: Union[Any, Callable[[], Any]]
) -> Tuple[Any, Callable[[Any], None]]:
    """
    Hook for state management
    
    Returns a stateful value and a function to update it.
    
    Args:
        initial_value: Initial state value or function that returns initial value
    
    Returns:
        tuple: (current_value, setter_function)
    
    Example:
        def Counter(props):
            count, set_count = use_state(0)
            return h('div', None,
                h('span', None, f"Count: {count}"),
                h('button', {'onClick': lambda _: set_count(count + 1)}, '+')
            )
    """
    global _hook_index
    component = _get_current_component()
    hook_index = _hook_index
    
    # Initialize hook if needed
    if hook_index >= len(component._hooks):
        initial = initial_value() if callable(initial_value) else initial_value
        component._hooks.append({
            'value': initial,
            'type': 'state'
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    def set_state(new_value: Union[Any, Callable[[Any], Any]]) -> None:
        """Update state value"""
        if callable(new_value):
            hook['value'] = new_value(hook['value'])
        else:
            hook['value'] = new_value
        
        # Trigger re-render
        if hasattr(component, '_schedule_update'):
            component._schedule_update()
    
    return hook['value'], set_state


def use_reducer(
    reducer: Callable[[Any, Any], Any],
    initial_state: Any,
    init: Optional[Callable[[Any], Any]] = None
) -> Tuple[Any, Callable[[Any], None]]:
    """
    Hook for complex state management with reducer
    
    Similar to Redux pattern.
    
    Args:
        reducer: Function (state, action) -> new_state
        initial_state: Initial state value
        init: Optional function to compute initial state lazily
    
    Returns:
        tuple: (state, dispatch_function)
    
    Example:
        def reducer(state, action):
            if action['type'] == 'INCREMENT':
                return {'count': state['count'] + 1}
            elif action['type'] == 'DECREMENT':
                return {'count': state['count'] - 1}
            return state
        
        def Counter(props):
            state, dispatch = use_reducer(reducer, {'count': 0})
            return h('div', None,
                h('span', None, f"Count: {state['count']}"),
                h('button', {'onClick': lambda _: dispatch({'type': 'INCREMENT'})}, '+')
            )
    """
    global _hook_index
    component = _get_current_component()
    hook_index = _hook_index
    
    # Initialize hook if needed
    if hook_index >= len(component._hooks):
        initial = init(initial_state) if init else initial_state
        component._hooks.append({
            'value': initial,
            'type': 'reducer',
            'reducer': reducer
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    def dispatch(action: Any) -> None:
        """Dispatch an action to the reducer"""
        hook['value'] = hook['reducer'](hook['value'], action)
        if hasattr(component, '_schedule_update'):
            component._schedule_update()
    
    return hook['value'], dispatch


def use_effect(
    setup: Callable[[], Optional[Callable[[], None]]],
    dependencies: Optional[List[Any]] = None
) -> None:
    """
    Hook for side effects
    
    Runs after render. Return a cleanup function to run before next effect or unmount.
    
    Args:
        setup: Function that returns cleanup function or None
        dependencies: List of values that trigger effect when changed
    
    Example:
        def Timer(props):
            seconds, set_seconds = use_state(0)
            
            @use_effect([])
            def setup_timer():
                def tick():
                    set_seconds(lambda s: s + 1)
                interval_id = setInterval(tick, 1000)
                return lambda: clearInterval(interval_id)
            
            return h('div', None, f"Seconds: {seconds}")
    """
    global _hook_index
    component = _get_current_component()
    hook_index = _hook_index
    
    # Initialize hook if needed
    if hook_index >= len(component._hooks):
        component._hooks.append({
            'type': 'effect',
            'cleanup': None,
            'deps': None
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    # Check if dependencies changed
    deps_changed = (
        hook['deps'] is None or
        dependencies is None or
        _deps_changed(hook['deps'], dependencies)
    )
    
    if deps_changed:
        # Run cleanup from previous effect
        if hook['cleanup']:
            try:
                hook['cleanup']()
            except Exception:
                pass
        
        # Run new setup
        hook['cleanup'] = setup()
        hook['deps'] = dependencies.copy() if dependencies else None


def use_layout_effect(
    setup: Callable[[], Optional[Callable[[], None]]],
    dependencies: Optional[List[Any]] = None
) -> None:
    """
    Hook for synchronous effects after DOM mutations
    
    Similar to use_effect but fires synchronously after all DOM mutations.
    Use for DOM measurements or mutations.
    
    Args:
        setup: Function that returns cleanup function or None
        dependencies: List of values that trigger effect when changed
    """
    # In this implementation, use_layout_effect behaves the same as use_effect
    # A real implementation would schedule this to run synchronously after paint
    use_effect(setup, dependencies)


def use_context(context: Any) -> Any:
    """
    Hook to consume context value
    
    Args:
        context: Context object created by create_context()
    
    Returns:
        Current context value
    
    Example:
        def Button(props):
            theme = use_context(ThemeContext)
            return h('button', {'className': f"btn-{theme}"}, 'Click')
    """
    global _hook_index
    component = _get_current_component()
    hook_index = _hook_index
    
    # Initialize hook if needed
    if hook_index >= len(component._hooks):
        component._hooks.append({
            'type': 'context',
            'context': context,
            'value': context._default_value
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    # Get current context value
    return hook['context']._get_value() if hasattr(hook['context'], '_get_value') else hook['value']


def use_ref(initial_value: Any = None) -> 'Ref':
    """
    Hook for mutable reference that persists across renders
    
    Changing ref.current does NOT trigger re-render.
    
    Args:
        initial_value: Initial value for ref.current
    
    Returns:
        Ref object with .current property
    
    Example:
        def TextInput(props):
            input_ref = use_ref(None)
            
            def focus():
                input_ref.current.focus()
            
            return h('input', {'ref': input_ref, 'type': 'text'})
    """
    global _hook_index
    component = _get_current_component()
    hook_index = _hook_index
    
    # Initialize hook if needed
    if hook_index >= len(component._hooks):
        ref = Ref()
        ref.current = initial_value
        component._hooks.append({
            'type': 'ref',
            'ref': ref
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    return hook['ref']


def use_memo(factory: Callable[[], Any], dependencies: List[Any]) -> Any:
    """
    Hook to memoize expensive computations
    
    Only recomputes when dependencies change.
    
    Args:
        factory: Function that computes the value
        dependencies: List of values that trigger recomputation
    
    Returns:
        Memoized value
    
    Example:
        def ExpensiveComponent(props):
            result = use_memo(
                lambda: expensive_computation(props['data']),
                [props['data']]
            )
            return h('div', None, result)
    """
    global _hook_index
    component = _get_current_component()
    hook_index = _hook_index
    
    # Initialize hook if needed
    if hook_index >= len(component._hooks):
        component._hooks.append({
            'type': 'memo',
            'value': factory(),
            'deps': dependencies.copy()
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    # Check if dependencies changed
    if _deps_changed(hook['deps'], dependencies):
        hook['value'] = factory()
        hook['deps'] = dependencies.copy()
    
    return hook['value']


def use_callback(callback: Callable, dependencies: List[Any]) -> Callable:
    """
    Hook to memoize callbacks
    
    Returns a memoized callback that only changes when dependencies change.
    Useful for passing callbacks to optimized child components.
    
    Args:
        callback: Function to memoize
        dependencies: List of values that trigger callback update
    
    Returns:
        Memoized callback
    
    Example:
        def Parent(props):
            def handle_click(item):
                print(f"Clicked {item}")
            
            memoized_click = use_callback(handle_click, [])
            return h(Child, {'onClick': memoized_click})
    """
    return use_memo(lambda: callback, dependencies)


def use_imperative_handle(
    ref: 'Ref',
    create_handle: Callable[[], Any],
    dependencies: Optional[List[Any]] = None
) -> None:
    """
    Hook to customize the instance value exposed to parent components
    
    Args:
        ref: Ref passed from parent
        create_handle: Function that returns object to expose
        dependencies: List of values that trigger handle update
    
    Example:
        def FancyInput(props, ref):
            input_ref = use_ref(None)
            
            use_imperative_handle(ref, lambda: {
                'focus': lambda: input_ref.current.focus(),
                'scrollIntoView': lambda: input_ref.current.scrollIntoView()
            }, [])
            
            return h('input', {'ref': input_ref})
    """
    def effect():
        if ref:
            ref.current = create_handle()
        return lambda: None
    
    use_effect(effect, dependencies)


def use_debug_value(value: Any, formatter: Optional[Callable[[Any], str]] = None) -> None:
    """
    Hook to display a label in DevTools
    
    Args:
        value: Value to display
        formatter: Optional function to format the value
    """
    # This is a no-op in production
    # DevTools would read this value
    pass


def use_id() -> str:
    """
    Hook to generate unique IDs for accessibility
    
    Returns:
        Unique ID string
    
    Example:
        def FormField(props):
            id = use_id()
            return h('div', None,
                h('label', {'htmlFor': id}, props['label']),
                h('input', {'id': id, 'type': 'text'})
            )
    """
    global _hook_index
    component = _get_current_component()
    hook_index = _hook_index
    
    # Initialize hook if needed
    if hook_index >= len(component._hooks):
        component._hooks.append({
            'type': 'id',
            'value': f"pyreact-{uuid.uuid4().hex[:8]}"
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    return hook['value']


def use_transition() -> Tuple[Callable[[Callable], None], bool]:
    """
    Hook for non-blocking UI updates
    
    Returns:
        tuple: (start_transition function, is_pending boolean)
    
    Example:
        def SearchResults(props):
            is_pending, start_transition = use_transition()
            
            def handle_change(e):
                start_transition(lambda: set_query(e.target.value))
            
            return h('div', None,
                h('input', {'onChange': handle_change}),
                is_pending and h('span', None, 'Loading...')
            )
    """
    global _hook_index
    component = _get_current_component()
    hook_index = _hook_index
    
    # Initialize hook if needed
    if hook_index >= len(component._hooks):
        component._hooks.append({
            'type': 'transition',
            'is_pending': False
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    def start_transition(callback: Callable) -> None:
        """Start a non-blocking transition"""
        hook['is_pending'] = True
        if hasattr(component, '_schedule_update'):
            component._schedule_update()
        
        # Execute callback asynchronously
        try:
            callback()
        finally:
            hook['is_pending'] = False
            if hasattr(component, '_schedule_update'):
                component._schedule_update()
    
    return start_transition, hook['is_pending']


def use_deferred_value(value: Any) -> Any:
    """
    Hook to defer a value for better performance
    
    Returns a deferred version that lags behind the current value.
    
    Args:
        value: Value to defer
    
    Returns:
        Deferred value
    """
    global _hook_index
    component = _get_current_component()
    hook_index = _hook_index
    
    # Initialize hook if needed
    if hook_index >= len(component._hooks):
        component._hooks.append({
            'type': 'deferred',
            'value': value,
            'deferred_value': value
        })
    
    hook = component._hooks[hook_index]
    _hook_index += 1
    
    # Update deferred value asynchronously
    if hook['value'] != value:
        hook['value'] = value
        # In a real implementation, this would be scheduled
        hook['deferred_value'] = value
    
    return hook['deferred_value']


class Ref:
    """Reference object for use_ref"""
    
    def __init__(self):
        self.current: Any = None
    
    def __repr__(self) -> str:
        return f"Ref(current={self.current!r})"


def _deps_changed(old_deps: Optional[List[Any]], new_deps: List[Any]) -> bool:
    """Check if dependencies have changed"""
    if old_deps is None:
        return True
    if len(old_deps) != len(new_deps):
        return True
    return any(a != b for a, b in zip(old_deps, new_deps))
