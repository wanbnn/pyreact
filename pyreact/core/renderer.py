"""DOM Renderer Module

This module handles rendering VNodes to actual DOM elements and managing the root container.
"""

from typing import Any, Callable, Dict, List, Optional, Union
import weakref
from .element import VNode
from .component import Component
from .reconciler import Reconciler


class Root:
    """
    Root container for a PyReact application.
    
    Manages the root DOM element and coordinates updates.
    """
    
    def __init__(self, container: Any, options: Optional[Dict[str, Any]] = None):
        """Initialize root container"""
        self.container = container
        self.options = options or {}
        self._reconciler = Reconciler()
        self._current_vnode: Optional[VNode] = None
        self._is_rendering: bool = False
        self._update_scheduled: bool = False
        self._callbacks: List[Callable] = []
    
    def render(self, element: Optional[VNode]) -> None:
        """Render an element to the container"""
        if element is None:
            self.unmount()
            return
        
        self._is_rendering = True
        try:
            if self._current_vnode is None:
                if not self.options.get('hydrate'):
                    self._clear_container()
                
                dom = self._reconciler.create_dom(element)
                self.container.append_child(dom)
            else:
                self._reconciler.diff(
                    self._current_vnode,
                    element,
                    self.container
                )
            
            self._current_vnode = element
        finally:
            self._is_rendering = False
        
        self._run_callbacks()
    
    def unmount(self) -> None:
        """Unmount the current tree"""
        if self._current_vnode:
            self._reconciler.unmount(self._current_vnode)
            self._clear_container()
            self._current_vnode = None
    
    def _clear_container(self) -> None:
        """Clear all children from container"""
        while self.container.first_child:
            self.container.remove_child(self.container.first_child)
    
    def _run_callbacks(self) -> None:
        """Run pending callbacks"""
        callbacks = self._callbacks.copy()
        self._callbacks.clear()
        for callback in callbacks:
            callback()
    
    def _schedule_callback(self, callback: Callable) -> None:
        """Schedule a callback to run after render"""
        self._callbacks.append(callback)


def create_root(container: Any, options: Optional[Dict[str, Any]] = None) -> Root:
    """Create a root for rendering"""
    return Root(container, options)


def render(element: VNode, container: Any) -> Root:
    """Render an element into a container (legacy API)"""
    while container.first_child:
        container.remove_child(container.first_child)
    
    root = create_root(container)
    root.render(element)
    return root


def hydrate(element: VNode, container: Any) -> Root:
    """Hydrate existing HTML with PyReact interactivity"""
    root = create_root(container, {'hydrate': True})
    root.render(element)
    return root


def unmount_component_at_node(container: Any) -> bool:
    """Unmount a PyReact component from a container"""
    while container.first_child:
        container.remove_child(container.first_child)
    return True


def find_dom_node(component: Component) -> Optional[Any]:
    """Find the DOM node associated with a component"""
    return component._dom_node
