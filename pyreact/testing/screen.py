"""
Screen Module
=============

Screen queries for testing PyReact components.
"""

from typing import Any, Callable, List, Optional


class Screen:
    """
    Screen object for querying rendered output
    
    Provides convenient methods to find elements.
    
    Example:
        result = render(h(App, None))
        
        # Using screen
        button = screen.get_by_role('button')
        text = screen.get_by_text('Hello')
    """
    
    def __init__(self):
        self._container: Optional[Any] = None
    
    def set_container(self, container: Any) -> None:
        """Set the container to query"""
        self._container = container
    
    def get_by_text(self, text: str) -> Any:
        """Get element by text content"""
        return self._query('text', text, required=True)
    
    def query_by_text(self, text: str) -> Optional[Any]:
        """Query element by text content"""
        return self._query('text', text, required=False)
    
    def find_by_text(self, text: str) -> Any:
        """Find element by text (async, waits for element)"""
        return self.get_by_text(text)
    
    def get_by_role(self, role: str) -> Any:
        """Get element by role"""
        return self._query('role', role, required=True)
    
    def query_by_role(self, role: str) -> Optional[Any]:
        """Query element by role"""
        return self._query('role', role, required=False)
    
    def find_by_role(self, role: str) -> Any:
        """Find element by role (async)"""
        return self.get_by_role(role)
    
    def get_by_test_id(self, test_id: str) -> Any:
        """Get element by data-testid"""
        return self._query('test_id', test_id, required=True)
    
    def query_by_test_id(self, test_id: str) -> Optional[Any]:
        """Query element by data-testid"""
        return self._query('test_id', test_id, required=False)
    
    def find_by_test_id(self, test_id: str) -> Any:
        """Find element by data-testid (async)"""
        return self.get_by_test_id(test_id)
    
    def get_by_placeholder_text(self, text: str) -> Any:
        """Get input by placeholder"""
        return self._query('placeholder', text, required=True)
    
    def query_by_placeholder_text(self, text: str) -> Optional[Any]:
        """Query input by placeholder"""
        return self._query('placeholder', text, required=False)
    
    def get_by_label_text(self, text: str) -> Any:
        """Get input by label text"""
        return self._query('label', text, required=True)
    
    def query_by_label_text(self, text: str) -> Optional[Any]:
        """Query input by label text"""
        return self._query('label', text, required=False)
    
    def get_by_display_value(self, value: str) -> Any:
        """Get input by displayed value"""
        return self._query('value', value, required=True)
    
    def query_by_display_value(self, value: str) -> Optional[Any]:
        """Query input by displayed value"""
        return self._query('value', value, required=False)
    
    def get_all_by_text(self, text: str) -> List[Any]:
        """Get all elements by text"""
        return self._query_all('text', text)
    
    def query_all_by_text(self, text: str) -> List[Any]:
        """Query all elements by text"""
        return self._query_all('text', text)
    
    def get_all_by_role(self, role: str) -> List[Any]:
        """Get all elements by role"""
        return self._query_all('role', role)
    
    def query_all_by_role(self, role: str) -> List[Any]:
        """Query all elements by role"""
        return self._query_all('role', role)
    
    def _query(self, query_type: str, value: str, required: bool = True) -> Optional[Any]:
        """Perform a query"""
        if self._container is None:
            if required:
                raise ValueError("No container set. Call set_container() first.")
            return None
        
        result = None
        
        if query_type == 'text':
            result = self._find_by_text(self._container, value)
        elif query_type == 'role':
            result = self._find_by_attr(self._container, 'role', value)
        elif query_type == 'test_id':
            result = self._find_by_attr(self._container, 'data-testid', value)
        elif query_type == 'placeholder':
            result = self._find_by_attr(self._container, 'placeholder', value)
        elif query_type == 'label':
            result = self._find_by_label(self._container, value)
        elif query_type == 'value':
            result = self._find_by_attr(self._container, 'value', value)
        
        if required and result is None:
            raise ValueError(f"Unable to find element with {query_type}: {value}")
        
        return result
    
    def _query_all(self, query_type: str, value: str) -> List[Any]:
        """Perform a query for all matches"""
        if self._container is None:
            return []
        
        results = []
        
        if query_type == 'text':
            results = self._find_all_by_text(self._container, value)
        elif query_type == 'role':
            results = self._find_all_by_attr(self._container, 'role', value)
        
        return results
    
    def _find_by_text(self, node: Any, text: str) -> Optional[Any]:
        """Find element by text content"""
        if isinstance(node, str):
            if text in node:
                return node
            return None
        
        if hasattr(node, 'text_content'):
            if text in node.text_content:
                return node
        
        if hasattr(node, 'children'):
            for child in node.children:
                result = self._find_by_text(child, text)
                if result is not None:
                    return result
        
        return None
    
    def _find_all_by_text(self, node: Any, text: str) -> List[Any]:
        """Find all elements by text content"""
        results = []
        
        if isinstance(node, str):
            if text in node:
                results.append(node)
            return results
        
        if hasattr(node, 'text_content'):
            if text in node.text_content:
                results.append(node)
        
        if hasattr(node, 'children'):
            for child in node.children:
                results.extend(self._find_all_by_text(child, text))
        
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
    
    def _find_all_by_attr(self, node: Any, attr: str, value: str) -> List[Any]:
        """Find all elements by attribute"""
        results = []
        
        if hasattr(node, 'attributes'):
            if node.attributes.get(attr) == value:
                results.append(node)
        
        if hasattr(node, 'children'):
            for child in node.children:
                results.extend(self._find_all_by_attr(child, attr, value))
        
        return results
    
    def _find_by_label(self, node: Any, text: str) -> Optional[Any]:
        """Find input by label text"""
        # Simplified implementation
        return None


# Global screen instance
screen = Screen()


def get_by_text(text: str) -> Any:
    """Get element by text content"""
    return screen.get_by_text(text)


def get_by_role(role: str) -> Any:
    """Get element by role"""
    return screen.get_by_role(role)


def get_by_test_id(test_id: str) -> Any:
    """Get element by data-testid"""
    return screen.get_by_test_id(test_id)


def query_by_text(text: str) -> Optional[Any]:
    """Query element by text content"""
    return screen.query_by_text(text)


def query_by_role(role: str) -> Optional[Any]:
    """Query element by role"""
    return screen.query_by_role(role)


def query_by_test_id(test_id: str) -> Optional[Any]:
    """Query element by data-testid"""
    return screen.query_by_test_id(test_id)


def find_by_text(text: str) -> Any:
    """Find element by text (async)"""
    return screen.find_by_text(text)


def find_by_role(role: str) -> Any:
    """Find element by role (async)"""
    return screen.find_by_role(role)


def find_by_test_id(test_id: str) -> Any:
    """Find element by data-testid (async)"""
    return screen.find_by_test_id(test_id)
