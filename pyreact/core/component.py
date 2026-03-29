"""
Component Base Class Module
===========================

This module defines the base Component class for stateful components
in PyReact, similar to React's React.Component.
"""

from typing import Any, Callable, Dict, List, Optional, Union, TYPE_CHECKING
from abc import ABC, abstractmethod
import weakref

if TYPE_CHECKING:
    from .element import VNode
    from .renderer import Root


class Component(ABC):
    """
    Base class for stateful components
    
    Components are the building blocks of PyReact applications.
    They manage their own state and define how to render themselves.
    
    Lifecycle Methods:
        - component_will_mount(): Called before mounting (deprecated)
        - component_did_mount(): Called after mounting
        - component_will_receive_props(): Called when props change (deprecated)
        - should_component_update(): Return False to prevent re-render
        - component_will_update(): Called before update (deprecated)
        - component_did_update(): Called after update
        - component_will_unmount(): Called before unmounting
        - component_did_catch(): Called when child throws error
    
    Example:
        class Counter(Component):
            def __init__(self, props):
                super().__init__(props)
                self.state = {'count': 0}
            
            def increment(self, event):
                self.set_state({'count': self.state['count'] + 1})
            
            def render(self):
                return h('div', {'className': 'counter'},
                    h('span', None, f"Count: {self.state['count']}"),
                    h('button', {'onClick': self.increment}, '+1')
                )
    """
    
    def __init__(self, props: Optional[Dict[str, Any]] = None):
        """
        Initialize component
        
        Args:
            props: Properties passed from parent component
        """
        self.props: Dict[str, Any] = props or {}
        self.state: Dict[str, Any] = {}
        self.context: Dict[str, Any] = {}
        
        # Internal state
        self._pending_state: Optional[Dict[str, Any]] = None
        self._pending_callbacks: List[Callable] = []
        self._is_mounted: bool = False
        self._is_rendering: bool = False
        self._root: Optional[weakref.ref] = None
        self._vnode: Optional['VNode'] = None
        self._dom_node: Optional[Any] = None
        self._updater: Optional[Callable] = None
        self._force_update: bool = False
    
    @abstractmethod
    def render(self) -> 'VNode':
        """
        Render the component
        
        Must be implemented by subclasses.
        
        Returns:
            VNode: Virtual DOM node representing the component's output
        """
        pass
    
    def set_state(
        self,
        new_state: Union[Dict[str, Any], Callable[[Dict[str, Any]], Dict[str, Any]]],
        callback: Optional[Callable] = None
    ) -> None:
        """
        Update component state
        
        Triggers a re-render after state update.
        
        Args:
            new_state: New state dict or function that returns new state
            callback: Optional callback called after update
        
        Example:
            # Direct state update
            self.set_state({'count': 1})
            
            # Functional update
            self.set_state(lambda state: {'count': state['count'] + 1})
        """
        if self._is_rendering:
            # Queue update for after render
            if callable(new_state):
                new_state = new_state(self.state)
            self._pending_state = {**self.state, **new_state}
            if callback:
                self._pending_callbacks.append(callback)
            return
        
        # Compute new state
        if callable(new_state):
            new_state = new_state(self.state)
        
        # Merge with pending state if exists
        if self._pending_state:
            self._pending_state = {**self._pending_state, **new_state}
        else:
            self._pending_state = {**self.state, **new_state}
        
        if callback:
            self._pending_callbacks.append(callback)
        
        # Schedule update
        self._schedule_update()
    
    def force_update(self, callback: Optional[Callable] = None) -> None:
        """
        Force a re-render of the component
        
        Args:
            callback: Optional callback called after update
        """
        self._force_update = True
        if callback:
            self._pending_callbacks.append(callback)
        self._schedule_update()
    
    def _schedule_update(self) -> None:
        """Schedule an update with the renderer"""
        if self._updater:
            self._updater(self)
    
    def _apply_state(self) -> bool:
        """
        Apply pending state changes
        
        Returns:
            bool: True if state was applied
        """
        if self._pending_state:
            self.state = self._pending_state
            self._pending_state = None
            return True
        return False
    
    def _run_callbacks(self) -> None:
        """Run pending callbacks after update"""
        callbacks = self._pending_callbacks.copy()
        self._pending_callbacks.clear()
        for callback in callbacks:
            callback()
    
    # Lifecycle Methods
    
    def component_will_mount(self) -> None:
        """
        Called before the component is mounted to the DOM
        
        Deprecated: Use component_did_mount instead
        """
        pass
    
    def component_did_mount(self) -> None:
        """
        Called after the component is mounted to the DOM
        
        Use this for:
        - Fetching data
        - Setting up subscriptions
        - DOM manipulation
        """
        pass
    
    def component_will_receive_props(self, next_props: Dict[str, Any]) -> None:
        """
        Called before new props are received
        
        Deprecated: Use get_derived_state_from_props instead
        
        Args:
            next_props: The new props
        """
        pass
    
    @staticmethod
    def get_derived_state_from_props(
        props: Dict[str, Any],
        state: Dict[str, Any]
    ) -> Optional[Dict[str, Any]]:
        """
        Called before render with new props
        
        Return an object to update state, or None to not update.
        
        Args:
            props: New props
            state: Current state
        
        Returns:
            dict or None: State updates
        """
        return None
    
    def should_component_update(
        self,
        next_props: Dict[str, Any],
        next_state: Dict[str, Any]
    ) -> bool:
        """
        Called before re-render to determine if update should proceed
        
        Override to implement custom comparison logic.
        
        Args:
            next_props: New props
            next_state: New state
        
        Returns:
            bool: True to proceed with update
        """
        return True
    
    def component_will_update(
        self,
        next_props: Dict[str, Any],
        next_state: Dict[str, Any]
    ) -> None:
        """
        Called before re-render
        
        Deprecated: Use component_did_update instead
        
        Args:
            next_props: New props
            next_state: New state
        """
        pass
    
    def component_did_update(
        self,
        prev_props: Dict[str, Any],
        prev_state: Dict[str, Any]
    ) -> None:
        """
        Called after re-render
        
        Use for:
        - DOM operations after update
        - Network requests (compare props first)
        
        Args:
            prev_props: Previous props
            prev_state: Previous state
        """
        pass
    
    def component_will_unmount(self) -> None:
        """
        Called before the component is unmounted
        
        Use for:
        - Cleaning up subscriptions
        - Canceling network requests
        - Invalidating timers
        """
        pass
    
    def component_did_catch(self, error: Exception, info: Dict[str, Any]) -> None:
        """
        Called when a child component throws an error
        
        Use for logging error information.
        
        Args:
            error: The error that was thrown
            info: Object with componentStack key
        """
        pass
    
    @staticmethod
    def get_derived_state_from_error(error: Exception) -> Optional[Dict[str, Any]]:
        """
        Called when a child component throws an error
        
        Return an object to update state.
        
        Args:
            error: The error that was thrown
        
        Returns:
            dict or None: State updates
        """
        return None
    
    def __repr__(self) -> str:
        return f"<{self.__class__.__name__}>"


class PureComponent(Component):
    """
    Component that implements should_component_update with shallow comparison
    
    Use PureComponent when you want to prevent unnecessary re-renders
    when props and state haven't changed.
    
    Example:
        class UserAvatar(PureComponent):
            def render(self):
                return h('img', {
                    'src': self.props['user']['avatar_url'],
                    'alt': self.props['user']['name']
                })
    """
    
    def should_component_update(
        self,
        next_props: Dict[str, Any],
        next_state: Dict[str, Any]
    ) -> bool:
        """
        Only re-render if props or state have changed (shallow comparison)
        
        Args:
            next_props: New props
            next_state: New state
        
        Returns:
            bool: True if props or state changed
        """
        return (
            not shallow_equal(self.props, next_props) or
            not shallow_equal(self.state, next_state)
        )


def shallow_equal(obj1: Dict[str, Any], obj2: Dict[str, Any]) -> bool:
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
