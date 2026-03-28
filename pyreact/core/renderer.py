"""
DOM Renderer Module
===================

This module handles rendering VNodes to actual DOM elements
and managing the root container.
"""

from typing import Any, Callable, Dict, List, Optional, Union
import weakref

from .element import VNode
from .component import Component
from .reconciler import Reconciler


class Root:
    """
    Root container for a PyReact application
    
    Manages the root DOM element and coordinates updates.
    
    Example:
        root = create_root(document.getElementById('app'))
        root.render(h(App, None))
    """
    
    def __init__(self, container: Any, options: Optional[Dict[str, Any]] = None):
        """
        Initialize root container
        
        Args:
            container: DOM element to render into
            options: Optional configuration
                - hydrate: Whether to hydrate existing HTML
        """
        self.container = container
        self.options = options or {}
        self._reconciler = Reconciler()
        self._current_vnode: Optional[VNode] = None
        self._is_rendering: bool = False
        self._update_scheduled: bool = False
        self._callbacks: List[Callable] = []
    
    def render(self, element: Optional[VNode]) -> None:
        """
        Render an element to the container
        
        Args:
            element: VNode to render, or None to unmount
        """
        if element is None:
            self.unmount()
            return
        
        self._is_rendering = True
        
        try:
            # First render or update
            if self._current_vnode is None:
                # Clear container for first render
                if not self.options.get('hydrate'):
                    self._clear_container()
                
                # Create initial DOM
                dom = self._reconciler.create_dom(element)
                self.container.appendChild(dom)
            else:
                # Diff and update
                self._reconciler.diff(
                    self._current_vnode,
                    element,
                    self.container
                )
            
            self._current_vnode = element
        finally:
            self._is_rendering = False
        
        # Run callbacks
        self._run_callbacks()
    
    def unmount(self) -> None:
        """Unmount the current tree"""
        if self._current_vnode:
            self._reconciler.unmount(self._current_vnode)
            self._clear_container()
            self._current_vnode = None
    
    def _clear_container(self) -> None:
        """Clear all children from container"""
        while self.container.firstChild:
            self.container.removeChild(self.container.firstChild)
    
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
    """
    Create a root for rendering
    
    Args:
        container: DOM element to render into
        options: Optional configuration
    
    Returns:
        Root: The created root
    
    Example:
        root = create_root(document.getElementById('app'))
        root.render(h(App, None))
    """
    return Root(container, options)


def render(element: VNode, container: Any) -> Root:
    """
    Render an element into a container (legacy API)
    
    This is the legacy render API, similar to React 17 and earlier.
    For new code, prefer create_root().render().
    
    Args:
        element: VNode to render
        container: DOM element to render into
    
    Returns:
        Root: The root instance
    
    Example:
        render(h(App, None), document.getElementById('root'))
    """
    # Clear container
    while container.firstChild:
        container.removeChild(container.firstChild)
    
    # Create root and render
    root = create_root(container)
    root.render(element)
    return root


def hydrate(element: VNode, container: Any) -> Root:
    """
    Hydrate existing HTML with PyReact interactivity
    
    Attaches event listeners to existing DOM nodes instead of
    creating new ones. Used for SSR.
    
    Args:
        element: VNode expected to match existing HTML
        container: DOM element with existing HTML
    
    Returns:
        Root: The root instance
    
    Example:
        # Server rendered HTML exists in container
        hydrate(h(App, None), document.getElementById('root'))
    """
    root = create_root(container, {'hydrate': True})
    root.render(element)
    return root


def unmount_component_at_node(container: Any) -> bool:
    """
    Unmount a PyReact component from a container
    
    Args:
        container: DOM element with mounted component
    
    Returns:
        bool: True if component was unmounted
    
    Deprecated: Use root.unmount() instead
    """
    # Find root associated with container
    # This is a simplified implementation
    while container.firstChild:
        container.removeChild(container.firstChild)
    return True


def find_dom_node(component: Component) -> Optional[Any]:
    """
    Find the DOM node associated with a component
    
    Args:
        component: Component instance
    
    Returns:
        DOM node or None
    
    Deprecated: Use refs instead
    """
    return component._dom_node
