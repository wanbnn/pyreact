"""
Memo Module
===========

This module implements memoization utilities for optimizing
component re-renders.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from functools import wraps
from .element import VNode


def memo(
    component: Callable,
    are_props_equal: Optional[Callable[[Dict, Dict], bool]] = None
) -> Callable:
    """
    Memoize a component to prevent unnecessary re-renders
    
    Similar to React.memo, wraps a component and only re-renders
    when props change.
    
    Args:
        component: Component function to memoize
        are_props_equal: Optional custom comparison function
    
    Returns:
        Memoized component
    
    Example:
        @memo
        def ExpensiveComponent(props):
            return h('div', None, expensive_computation(props['data']))
        
        # With custom comparison
        @memo(are_props_equal=lambda prev, next: prev['id'] == next['id'])
        def UserAvatar(props):
            return h('img', {'src': props['user']['avatar']})
    """
    @wraps(component)
    def memoized(props: Dict[str, Any]) -> VNode:
        return component(props)

    memoized._component = component
    memoized._pyreact_memo_compare = are_props_equal or _shallow_equal
    
    return memoized


def lazy(loader: Callable[[], Any]) -> Callable:
    """
    Lazy load a component
    
    Returns a component that is loaded on demand.
    
    Args:
        loader: Async function that returns the component module
    
    Returns:
        Lazy component
    
    Example:
        HeavyComponent = lazy(lambda: import_module('./HeavyComponent.py'))
        
        h(Suspense, {'fallback': h('div', None, 'Loading...')},
            h(HeavyComponent, None)
        )
    """
    from .component import Component
    
    class LazyComponent(Component):
        """Lazy-loaded component wrapper"""
        
        def __init__(self, props):
            super().__init__(props)
            self.state = {
                'loaded': False,
                'component': None,
                'error': None
            }
        
        def component_did_mount(self):
            """Load the component"""
            import asyncio
            import inspect

            async def resolve():
                try:
                    loaded = loader()
                    module = await loaded if inspect.isawaitable(loaded) else loaded
                    component = getattr(module, 'default', module)
                    self.set_state({
                        'loaded': True,
                        'component': component
                    })
                except Exception as e:
                    self.set_state({'error': e})
            
            try:
                loop = asyncio.get_running_loop()
            except RuntimeError:
                asyncio.run(resolve())
            else:
                loop.create_task(resolve())
        
        def render(self):
            if self.state['error']:
                return self.props.get('fallback', VNode('div', None, ['Error loading component']))
            
            if not self.state['loaded']:
                return self.props.get('loading', VNode('div', None, ['Loading...']))
            
            Component = self.state['component']
            return VNode(Component, self.props)
    
    return LazyComponent


class Suspense:
    """
    Suspense boundary for handling loading states
    
    Wraps components that may suspend (like lazy components)
    and shows a fallback while loading.
    
    Example:
        h(Suspense, {'fallback': h('div', None, 'Loading...')},
            h(LazyComponent, None)
        )
    """
    
    def __init__(self, props: Dict[str, Any]):
        self.props = props
        self.fallback = props.get('fallback', VNode('div', None, ['Loading...']))
        self.children = props.get('children', [])
    
    def render(self) -> VNode:
        """Render fallback or children"""
        # In a real implementation, this would check if children are suspended
        return self.children if self.children else self.fallback


def _shallow_equal(obj1: Dict[str, Any], obj2: Dict[str, Any]) -> bool:
    """
    Perform shallow comparison of two objects
    
    Args:
        obj1: First object
        obj2: Second object
    
    Returns:
        bool: True if objects are shallowly equal
    """
    if obj1 is obj2:
        return True
    
    if len(obj1) != len(obj2):
        return False
    
    for key in obj1:
        if key not in obj2 or obj1[key] != obj2[key]:
            return False
    
    return True


def are_props_shallow_equal(prev_props: Dict, next_props: Dict) -> bool:
    """
    Check if props are shallowly equal
    
    Args:
        prev_props: Previous props
        next_props: Next props
    
    Returns:
        bool: True if props are shallowly equal
    """
    return _shallow_equal(prev_props, next_props)


def shallow_compare(
    prev_props: Dict,
    next_props: Dict,
    prev_state: Optional[Dict] = None,
    next_state: Optional[Dict] = None
) -> bool:
    """
    Compare props and state for PureComponent
    
    Args:
        prev_props: Previous props
        next_props: Next props
        prev_state: Previous state (optional)
        next_state: Next state (optional)
    
    Returns:
        bool: True if props and state are shallowly equal
    """
    props_equal = _shallow_equal(prev_props, next_props)
    
    if prev_state is not None and next_state is not None:
        state_equal = _shallow_equal(prev_state, next_state)
        return props_equal and state_equal
    
    return props_equal
