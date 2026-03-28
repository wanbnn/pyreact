"""
Hydration Module
================

This module implements client-side hydration for server-rendered HTML.
"""

from typing import Any, Dict, Optional


class HydrationMismatchError(Exception):
    """
    Error raised when server HTML doesn't match client render
    
    This can happen when:
    - Server and client render different content
    - Browser fixes invalid HTML
    - Data changes between render and hydration
    """
    
    def __init__(self, message: str, server_html: str = '', client_html: str = ''):
        self.message = message
        self.server_html = server_html
        self.client_html = client_html
        super().__init__(message)


def hydrate(element: Any, container: Any) -> Any:
    """
    Hydrate server-rendered HTML with PyReact interactivity
    
    Attaches event listeners and initializes state without
    recreating the DOM.
    
    Args:
        element: VNode expected to match server HTML
        container: DOM element with server-rendered HTML
    
    Returns:
        Root: The root instance
    
    Example:
        # Server rendered HTML exists in container
        hydrate(h(App, None), document.getElementById('root'))
    
    Raises:
        HydrationMismatchError: If server HTML doesn't match client
    """
    from .core.renderer import create_root
    
    # Create root with hydration mode
    root = create_root(container, {'hydrate': True})
    root.render(element)
    
    return root


def hydrate_root(container: Any, element: Any) -> Any:
    """
    Alias for hydrate (React 18 API)
    
    Args:
        container: DOM element with server-rendered HTML
        element: VNode expected to match server HTML
    
    Returns:
        Root: The root instance
    """
    return hydrate(element, container)


class HydrationContext:
    """
    Context for tracking hydration state
    """
    
    def __init__(self):
        self.is_hydrating: bool = False
        self.errors: list = []
        self.warnings: list = []
    
    def start_hydration(self) -> None:
        """Mark hydration as started"""
        self.is_hydrating = True
    
    def end_hydration(self) -> None:
        """Mark hydration as ended"""
        self.is_hydrating = False
    
    def add_error(self, error: Exception) -> None:
        """Add a hydration error"""
        self.errors.append(error)
    
    def add_warning(self, message: str) -> None:
        """Add a hydration warning"""
        self.warnings.append(message)


def check_hydration_mismatch(
    server_node: Any,
    client_node: Any,
    path: str = ''
) -> Optional[HydrationMismatchError]:
    """
    Check if server and client nodes match
    
    Args:
        server_node: Server-rendered DOM node
        client_node: Client-rendered VNode
        path: Current path in tree
    
    Returns:
        HydrationMismatchError if mismatch, None otherwise
    """
    # Check node type
    if type(server_node) != type(client_node):
        return HydrationMismatchError(
            f"Node type mismatch at {path}: "
            f"server={type(server_node).__name__}, "
            f"client={type(client_node).__name__}"
        )
    
    # Check tag name for elements
    if hasattr(server_node, 'tagName') and hasattr(client_node, 'type'):
        if server_node.tagName.lower() != client_node.type.lower():
            return HydrationMismatchError(
                f"Tag mismatch at {path}: "
                f"server={server_node.tagName}, "
                f"client={client_node.type}"
            )
    
    # Check text content
    if isinstance(server_node, str) and isinstance(client_node, str):
        if server_node != client_node:
            return HydrationMismatchError(
                f"Text mismatch at {path}: "
                f"server={server_node!r}, "
                f"client={client_node!r}"
            )
    
    return None


def suppress_hydration_warning() -> None:
    """
    Suppress hydration warnings for the current component
    
    Use when you know server and client will differ intentionally.
    """
    # In a real implementation, this would set a flag on the current component
    pass


def use_hydration() -> Dict[str, bool]:
    """
    Hook to check hydration state
    
    Returns:
        dict: {'is_hydrating': bool, 'is_hydrated': bool}
    """
    # Simplified implementation
    return {
        'is_hydrating': False,
        'is_hydrated': True
    }


class HydrationManager:
    """
    Manager for hydration process
    """
    
    def __init__(self):
        self._context = HydrationContext()
        self._hydrated_roots: Dict[int, Any] = {}
    
    def hydrate_root(self, container: Any, element: Any) -> Any:
        """
        Hydrate a root container
        
        Args:
            container: DOM element
            element: VNode
        
        Returns:
            Root instance
        """
        self._context.start_hydration()
        
        try:
            root = hydrate(element, container)
            self._hydrated_roots[id(container)] = root
            return root
        finally:
            self._context.end_hydration()
    
    def get_errors(self) -> list:
        """Get hydration errors"""
        return self._context.errors.copy()
    
    def get_warnings(self) -> list:
        """Get hydration warnings"""
        return self._context.warnings.copy()
    
    def has_errors(self) -> bool:
        """Check if there were hydration errors"""
        return len(self._context.errors) > 0


# Global hydration manager
_hydration_manager = HydrationManager()


def get_hydration_manager() -> HydrationManager:
    """Get the global hydration manager"""
    return _hydration_manager
