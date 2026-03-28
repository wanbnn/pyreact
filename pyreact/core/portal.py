"""
Portal Module
=============

This module implements Portals for rendering children into a different
DOM node than their parent.
"""

from typing import Any, Dict, Optional
from .element import VNode


class Portal:
    """
    Portal for rendering into a different DOM container
    
    Portals provide a way to render children into a DOM node that exists
    outside the parent component's DOM hierarchy.
    
    Example:
        def Modal(props):
            return create_portal(
                h('div', {'className': 'modal-overlay'},
                    h('div', {'className': 'modal-content'},
                        props['children']
                    )
                ),
                document.body
            )
    """
    
    def __init__(self, children: Any, container: Any):
        """
        Initialize portal
        
        Args:
            children: VNode or list of VNodes to render
            container: DOM node to render into
        """
        self.children = children
        self.container = container
        self._dom_nodes: list = []
    
    def __repr__(self) -> str:
        return f"Portal(container={self.container!r})"


def create_portal(children: Any, container: Any) -> Portal:
    """
    Create a portal to render children into a different container
    
    Args:
        children: VNode or list of VNodes to render
        container: DOM node to render into
    
    Returns:
        Portal: A portal object
    
    Example:
        def Tooltip(props):
            return create_portal(
                h('div', {'className': 'tooltip'},
                    props['content']
                ),
                document.getElementById('tooltip-root')
            )
    """
    return Portal(children, container)


def is_portal(element: Any) -> bool:
    """
    Check if an element is a portal
    
    Args:
        element: Element to check
    
    Returns:
        bool: True if element is a portal
    """
    return isinstance(element, Portal)


def unmount_portal(portal: Portal) -> None:
    """
    Unmount a portal's children
    
    Args:
        portal: Portal to unmount
    """
    for dom_node in portal._dom_nodes:
        if dom_node and dom_node.parentNode:
            dom_node.parentNode.removeChild(dom_node)
    portal._dom_nodes.clear()


def render_portal(portal: Portal, renderer: Any) -> None:
    """
    Render a portal's children into its container
    
    Args:
        portal: Portal to render
        renderer: Renderer instance
    """
    # Clear existing content
    while portal.container.firstChild:
        portal.container.removeChild(portal.container.firstChild)
    
    # Render children
    if isinstance(portal.children, VNode):
        dom = renderer.create_dom(portal.children)
        portal.container.appendChild(dom)
        portal._dom_nodes.append(dom)
    elif isinstance(portal.children, list):
        for child in portal.children:
            if isinstance(child, VNode):
                dom = renderer.create_dom(child)
                portal.container.appendChild(dom)
                portal._dom_nodes.append(dom)


class PortalManager:
    """
    Manager for all portals in the application
    """
    
    def __init__(self):
        self._portals: Dict[int, Portal] = {}
    
    def register(self, portal: Portal) -> int:
        """Register a portal"""
        portal_id = id(portal)
        self._portals[portal_id] = portal
        return portal_id
    
    def unregister(self, portal: Portal) -> None:
        """Unregister a portal"""
        portal_id = id(portal)
        if portal_id in self._portals:
            del self._portals[portal_id]
    
    def get_portal(self, portal_id: int) -> Optional[Portal]:
        """Get a portal by ID"""
        return self._portals.get(portal_id)
    
    def unmount_all(self) -> None:
        """Unmount all portals"""
        for portal in self._portals.values():
            unmount_portal(portal)
        self._portals.clear()


# Global portal manager
_portal_manager = PortalManager()


def get_portal_manager() -> PortalManager:
    """Get the global portal manager"""
    return _portal_manager
