"""
Test Renderer Module
====================

Test renderer for PyReact components.
"""

from typing import Any, Callable, Dict, List, Optional, Union
from .element import VNode
from .component import Component


class RenderResult:
    """
    Result of rendering a component for testing
    
    Provides methods to query the rendered output.
    """
    
    def __init__(self, container: Any, vnode: VNode):
        self.container = container
        self.vnode = vnode
        self._component = vnode._component_instance if hasattr(vnode, '_component_instance') else None
    
    def query_by_text(self, text: str) -> Optional[Any]:
        """Find element by text content"""
        return self._find_by_text(self.container, text)
    
    def get_by_text(self, text: str) -> Any:
        """Find element by text content (throws if not found)"""
        result = self.query_by_text(text)
        if result is None:
            raise ValueError(f"Unable to find element with text: {text}")
        return result
    
    def query_by_test_id(self, test_id: str) -> Optional[Any]:
        """Find element by data-testid"""
        return self._find_by_attr(self.container, 'data-testid', test_id)
    
    def get_by_test_id(self, test_id: str) -> Any:
        """Find element by data-testid (throws if not found)"""
        result = self.query_by_test_id(test_id)
        if result is None:
            raise ValueError(f"Unable to find element with test id: {test_id}")
        return result
    
    def query_by_role(self, role: str) -> Optional[Any]:
        """Find element by role attribute"""
        return self._find_by_attr(self.container, 'role', role)
    
    def get_by_role(self, role: str) -> Any:
        """Find element by role (throws if not found)"""
        result = self.query_by_role(role)
        if result is None:
            raise ValueError(f"Unable to find element with role: {role}")
        return result
    
    def query_all_by_text(self, text: str) -> List[Any]:
        """Find all elements by text content"""
        return self._find_all_by_text(self.container, text)
    
    def get_all_by_text(self, text: str) -> List[Any]:
        """Find all elements by text content (throws if none found)"""
        results = self.query_all_by_text(text)
        if not results:
            raise ValueError(f"Unable to find elements with text: {text}")
        return results
    
    def rerender(self, vnode: VNode) -> None:
        """Re-render with new props"""
        # In a real implementation, this would update the existing tree
        pass
    
    def unmount(self) -> None:
        """Unmount the component"""
        if self._component and hasattr(self._component, 'component_will_unmount'):
            self._component.component_will_unmount()
    
    def _find_by_text(self, node: Any, text: str) -> Optional[Any]:
        """Recursively find element by text"""
        if isinstance(node, str):
            if text in node:
                return node
            return None
        
        # Check children
        if hasattr(node, 'children'):
            for child in node.children:
                result = self._find_by_text(child, text)
                if result is not None:
                    return result
        
        # Check text content
        if hasattr(node, 'text_content'):
            if text in node.text_content:
                return node
        
        return None
    
    def _find_all_by_text(self, node: Any, text: str) -> List[Any]:
        """Recursively find all elements by text"""
        results = []
        
        if isinstance(node, str):
            if text in node:
                results.append(node)
            return results
        
        if hasattr(node, 'children'):
            for child in node.children:
                results.extend(self._find_all_by_text(child, text))
        
        if hasattr(node, 'text_content'):
            if text in node.text_content:
                results.append(node)
        
        return results
    
    def _find_by_attr(self, node: Any, attr: str, value: str) -> Optional[Any]:
        """Find element by attribute"""
        if hasattr(node, 'attributes'):
            if node.attributes.get(attr) == value:
                return node
        
        if hasattr(node, 'children'):
            for child in node.children:
                result = self._find_by_attr(child, attr, value)
                if result is not None:
                    return result
        
        return None


def render(
    element: Union[VNode, Component],
    options: Optional[Dict] = None
) -> RenderResult:
    """
    Render a component for testing
    
    Args:
        element: VNode or Component to render
        options: Optional render options
    
    Returns:
        RenderResult: Test result object
    
    Example:
        result = render(h(Counter, None))
        button = result.get_by_text('+1')
        fire_event.click(button)
        assert result.get_by_text('Count: 1')
    """
    from .dom.dom_operations import document
    
    options = options or {}
    
    # Create container
    container = options.get('container', document.create_element('div'))
    
    # Render element
    if isinstance(element, VNode):
        vnode = element
    elif isinstance(element, Component):
        vnode = element.render()
    else:
        raise ValueError("Invalid element type")
    
    return RenderResult(container, vnode)


def cleanup() -> None:
    """
    Clean up after tests
    
    Removes all mounted components.
    """
    # In a real implementation, this would unmount all components
    pass


def act(callback: Callable) -> None:
    """
    Perform an action that updates state
    
    Use to wrap state updates in tests.
    
    Args:
        callback: Function to execute
    
    Example:
        def test_counter():
            result = render(h(Counter, None))
            button = result.get_by_text('+1')
            
            act(lambda: fire_event.click(button))
            
            assert result.get_by_text('Count: 1')
    """
    # Execute callback
    callback()
    
    # In a real implementation, this would flush pending updates
    pass


def render_to_json(element: VNode) -> Dict:
    """
    Render element to JSON for snapshot testing
    
    Args:
        element: VNode to render
    
    Returns:
        dict: JSON representation
    
    Example:
        tree = render_to_json(h(Button, {'variant': 'primary'}, 'Click'))
        assert tree == {
            'type': 'button',
            'props': {'className': 'btn btn-primary'},
            'children': ['Click']
        }
    """
    if isinstance(element, str):
        return element
    
    return {
        'type': element.type if isinstance(element.type, str) else element.type.__name__,
        'props': element.props.copy(),
        'children': [render_to_json(child) for child in element.children]
    }
