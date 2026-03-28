"""
Error Boundary Module
=====================

This module implements Error Boundaries for catching errors
in child components.
"""

from typing import Any, Callable, Dict, Optional
from .component import Component
from .element import VNode


class ErrorBoundary(Component):
    """
    Error Boundary component
    
    Catches errors in child components and displays a fallback UI.
    
    Example:
        h(ErrorBoundary, {
            'fallback': h('div', None, 'Something went wrong!')
        },
            h(RiskyComponent, None)
        )
    """
    
    def __init__(self, props: Optional[Dict[str, Any]] = None):
        super().__init__(props)
        self.state = {
            'has_error': False,
            'error': None,
            'error_info': None
        }
    
    @staticmethod
    def get_derived_state_from_error(error: Exception) -> Dict[str, Any]:
        """
        Update state when an error is thrown
        
        Args:
            error: The error that was thrown
        
        Returns:
            dict: State updates
        """
        return {
            'has_error': True,
            'error': error
        }
    
    def component_did_catch(self, error: Exception, info: Dict[str, Any]) -> None:
        """
        Log error information
        
        Args:
            error: The error that was thrown
            info: Object with componentStack key
        """
        # Log error (could be sent to error reporting service)
        print(f"ErrorBoundary caught an error: {error}")
        if 'componentStack' in info:
            print(f"Component stack: {info['componentStack']}")
    
    def render(self) -> VNode:
        """Render fallback or children"""
        if self.state['has_error']:
            fallback = self.props.get('fallback')
            if fallback:
                return fallback
            
            # Default fallback
            return VNode('div', {'className': 'error-boundary'}, [
                VNode('h2', None, ['Something went wrong.']),
                VNode('p', None, [str(self.state['error'])])
            ])
        
        return self.props.get('children', VNode('div', None, []))


def with_error_boundary(
    component: Callable,
    fallback: Optional[VNode] = None,
    on_error: Optional[Callable[[Exception, Dict], None]] = None
) -> Callable:
    """
    Higher-order component that wraps a component with an ErrorBoundary
    
    Args:
        component: Component to wrap
        fallback: Fallback UI to show on error
        on_error: Callback when error occurs
    
    Returns:
        Wrapped component
    
    Example:
        @with_error_boundary(fallback=h('div', None, 'Error!'))
        def RiskyComponent(props):
            # May throw an error
            return h('div', None, risky_operation())
    """
    class WrappedErrorBoundary(ErrorBoundary):
        def component_did_catch(self, error, info):
            super().component_did_catch(error, info)
            if on_error:
                on_error(error, info)
    
    def wrapper(props):
        return VNode(WrappedErrorBoundary, {
            'fallback': fallback
        }, [VNode(component, props)])
    
    return wrapper


class ErrorInfo:
    """
    Error information object passed to component_did_catch
    """
    
    def __init__(self, component_stack: str = ''):
        self.component_stack = component_stack
    
    def to_dict(self) -> Dict[str, Any]:
        return {
            'componentStack': self.component_stack
        }


def capture_error(error: Exception, component_stack: str = '') -> Dict[str, Any]:
    """
    Capture error information
    
    Args:
        error: The error that was thrown
        component_stack: Component stack trace
    
    Returns:
        dict: Error information
    """
    return {
        'error': error,
        'errorInfo': ErrorInfo(component_stack).to_dict()
    }
