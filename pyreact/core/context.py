"""
Context API Module
==================

This module implements the Context API for sharing state across components
without prop drilling.
"""

from typing import Any, Callable, Dict, List, Optional
import uuid


class Context:
    """
    Context object for sharing state
    
    Created by create_context() function.
    
    Attributes:
        _id: Unique identifier for this context
        _default_value: Default value when no Provider is found
        _providers: Stack of provider values
    """
    
    def __init__(self, default_value: Any = None):
        self._id = f"context-{uuid.uuid4().hex[:8]}"
        self._default_value = default_value
        self._providers: Dict[int, Any] = {}
        self._provider_stack: List[int] = []
    
    def _get_value(self) -> Any:
        """Get current context value"""
        if self._provider_stack:
            provider_id = self._provider_stack[-1]
            return self._providers.get(provider_id, self._default_value)
        return self._default_value
    
    def _push_provider(self, provider_id: int, value: Any) -> None:
        """Push a provider value onto the stack"""
        self._providers[provider_id] = value
        self._provider_stack.append(provider_id)
    
    def _pop_provider(self, provider_id: int) -> None:
        """Pop a provider value from the stack"""
        if provider_id in self._providers:
            del self._providers[provider_id]
        if provider_id in self._provider_stack:
            self._provider_stack.remove(provider_id)
    
    class Provider:
        """
        Provider component for context
        
        Example:
            h(ThemeContext.Provider, {'value': 'dark'},
                h(App, None)
            )
        """
        
        def __init__(self, context: 'Context', props: Dict[str, Any]):
            self.context = context
            self.props = props
            self._id = id(self)
            self._children = props.get('children', [])
        
        def render(self) -> Any:
            """Provider doesn't render anything, just provides value"""
            return self._children
        
        def __enter__(self):
            """Context manager support"""
            value = self.props.get('value', self.context._default_value)
            self.context._push_provider(self._id, value)
            return self
        
        def __exit__(self, *args):
            """Context manager support"""
            self.context._pop_provider(self._id)
    
    class Consumer:
        """
        Consumer component for context
        
        Example:
            h(ThemeContext.Consumer, None,
                lambda theme: h('div', None, f"Theme: {theme}")
            )
        """
        
        def __init__(self, context: 'Context', props: Dict[str, Any]):
            self.context = context
            self.props = props
        
        def render(self) -> Any:
            """Call children function with context value"""
            children = self.props.get('children')
            if callable(children):
                return children(self.context._get_value())
            return children


def create_context(default_value: Any = None) -> Context:
    """
    Create a new Context object
    
    Args:
        default_value: Default value when no Provider is found
    
    Returns:
        Context: The created context
    
    Example:
        ThemeContext = create_context('light')
        
        def App():
            return h(ThemeContext.Provider, {'value': 'dark'},
                h(Toolbar, None)
            )
        
        def Toolbar():
            theme = use_context(ThemeContext)
            return h('div', {'className': f"toolbar-{theme}"}, '...')
    """
    return Context(default_value)


def use_context(context: Context) -> Any:
    """
    Hook to consume context value
    
    This is a re-export from hooks.py for convenience.
    
    Args:
        context: Context object created by create_context()
    
    Returns:
        Current context value
    """
    from .hooks import use_context as _use_context
    return _use_context(context)


class ContextManager:
    """
    Manager for all contexts in the application
    
    Handles nested providers and context updates.
    """
    
    def __init__(self):
        self._contexts: Dict[str, Context] = {}
    
    def register(self, context: Context) -> None:
        """Register a context"""
        self._contexts[context._id] = context
    
    def unregister(self, context: Context) -> None:
        """Unregister a context"""
        if context._id in self._contexts:
            del self._contexts[context._id]
    
    def get_context(self, context_id: str) -> Optional[Context]:
        """Get a context by ID"""
        return self._contexts.get(context_id)


# Global context manager
_context_manager = ContextManager()


def get_context_manager() -> ContextManager:
    """Get the global context manager"""
    return _context_manager
