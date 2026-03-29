"""
DOM Operations Module
=====================

This module provides low-level DOM manipulation functions.
These are platform-agnostic and can be adapted for different environments.
"""

from typing import Any, Callable, Dict, Optional


# Platform-specific DOM implementation
# In a real implementation, this would use a JavaScript bridge

class DOMNode:
    """Base class for DOM nodes"""
    
    def __init__(self, node_type: str):
        self.node_type = node_type
        self.parent_node: Optional['DOMNode'] = None
        self.child_nodes: list = []
    
    def append_child(self, child: 'DOMNode') -> 'DOMNode':
        """Append a child node"""
        child.parent_node = self
        self.child_nodes.append(child)
        return child
    
    def remove_child(self, child: 'DOMNode') -> 'DOMNode':
        """Remove a child node"""
        if child in self.child_nodes:
            child.parent_node = None
            self.child_nodes.remove(child)
        return child
    
    def insert_before(self, new_node: 'DOMNode', ref_node: Optional['DOMNode']) -> 'DOMNode':
        """Insert a node before a reference node"""
        new_node.parent_node = self
        if ref_node is None:
            self.child_nodes.append(new_node)
        else:
            index = self.child_nodes.index(ref_node)
            self.child_nodes.insert(index, new_node)
        return new_node


class Element(DOMNode):
    """DOM Element"""
    
    def __init__(self, tag_name: str):
        super().__init__('element')
        self.tag_name = tag_name.lower()
        self.attributes: Dict[str, str] = {}
        self.style: Dict[str, str] = {}
        self._event_listeners: Dict[str, list] = {}
        self._text_content: str = ''
    
    def set_attribute(self, name: str, value: str) -> None:
        """Set an attribute"""
        self.attributes[name] = value
    
    def get_attribute(self, name: str) -> Optional[str]:
        """Get an attribute"""
        return self.attributes.get(name)
    
    def remove_attribute(self, name: str) -> None:
        """Remove an attribute"""
        if name in self.attributes:
            del self.attributes[name]
    
    def set_style(self, name: str, value: str) -> None:
        """Set a style property"""
        self.style[name] = value
    
    def add_event_listener(self, event_type: str, listener: Callable) -> None:
        """Add an event listener"""
        if event_type not in self._event_listeners:
            self._event_listeners[event_type] = []
        self._event_listeners[event_type].append(listener)
    
    def remove_event_listener(self, event_type: str, listener: Callable) -> None:
        """Remove an event listener"""
        if event_type in self._event_listeners:
            if listener in self._event_listeners[event_type]:
                self._event_listeners[event_type].remove(listener)
    
    def set_inner_html(self, html: str) -> None:
        """Set inner HTML"""
        self._text_content = html
        self.child_nodes.clear()
    
    def insert_child(self, child: 'DOMNode', index: int) -> None:
        """Insert a child at a specific index"""
        child.parent_node = self
        self.child_nodes.insert(index, child)
    
    def remove_child_at(self, index: int) -> None:
        """Remove a child at a specific index"""
        if 0 <= index < len(self.child_nodes):
            child = self.child_nodes.pop(index)
            child.parent_node = None
    
    def replace_child_at(self, new_child: 'DOMNode', index: int) -> None:
        """Replace a child at a specific index"""
        if 0 <= index < len(self.child_nodes):
            old_child = self.child_nodes[index]
            old_child.parent_node = None
            new_child.parent_node = self
            self.child_nodes[index] = new_child
    
    def move_child(self, old_index: int, new_index: int) -> None:
        """Move a child from old_index to new_index"""
        if 0 <= old_index < len(self.child_nodes) and 0 <= new_index < len(self.child_nodes):
            child = self.child_nodes.pop(old_index)
            self.child_nodes.insert(new_index, child)
    
    @property
    def first_child(self) -> Optional['DOMNode']:
        """Get first child"""
        return self.child_nodes[0] if self.child_nodes else None
    
    @property
    def inner_html(self) -> str:
        """Get inner HTML"""
        return self._text_content
    
    @inner_html.setter
    def inner_html(self, value: str):
        """Set inner HTML"""
        self._text_content = value
        self.child_nodes.clear()
    
    def get_element_by_id(self, id: str) -> Optional['Element']:
        """Find element by ID"""
        if self.attributes.get('id') == id:
            return self
        for child in self.child_nodes:
            if isinstance(child, Element):
                result = child.get_element_by_id(id)
                if result:
                    return result
        return None
    
    def query_selector(self, selector: str) -> Optional['Element']:
        """Query selector (simplified)"""
        # Simplified implementation
        for child in self.child_nodes:
            if isinstance(child, Element):
                if selector.startswith('#'):
                    if child.attributes.get('id') == selector[1:]:
                        return child
                elif selector.startswith('.'):
                    class_name = selector[1:]
                    if class_name in child.attributes.get('class', '').split():
                        return child
                elif child.tag_name == selector.lower():
                    return child
        return None
    
    def query_selector_all(self, selector: str) -> list:
        """Query all matching elements"""
        results = []
        for child in self.child_nodes:
            if isinstance(child, Element):
                if selector.startswith('#'):
                    if child.attributes.get('id') == selector[1:]:
                        results.append(child)
                elif selector.startswith('.'):
                    class_name = selector[1:]
                    if class_name in child.attributes.get('class', '').split():
                        results.append(child)
                elif child.tag_name == selector.lower():
                    results.append(child)
                results.extend(child.query_selector_all(selector))
        return results
    
    def focus(self) -> None:
        """Focus the element"""
        pass
    
    def blur(self) -> None:
        """Blur the element"""
        pass
    
    def click(self) -> None:
        """Click the element"""
        pass
    
    def scroll_into_view(self) -> None:
        """Scroll element into view"""
        pass
    
    def get_bounding_client_rect(self) -> Dict[str, float]:
        """Get element dimensions"""
        return {
            'x': 0, 'y': 0,
            'width': 0, 'height': 0,
            'top': 0, 'right': 0,
            'bottom': 0, 'left': 0
        }
    
    def __repr__(self) -> str:
        return f"<{self.tag_name}>"


class TextNode(DOMNode):
    """Text node"""
    
    def __init__(self, text: str):
        super().__init__('text')
        self.text_content = text
    
    def __repr__(self) -> str:
        return f"#text: {self.text_content[:20]}..."


class CommentNode(DOMNode):
    """Comment node"""
    
    def __init__(self, text: str):
        super().__init__('comment')
        self.text_content = text


class Document(Element):
    """Document object"""
    
    def __init__(self):
        super().__init__('html')
        self.node_type = 'document'
        self.body = Element('body')
        self.head = Element('head')
        self.append_child(self.head)
        self.append_child(self.body)
    
    def create_element(self, tag_name: str) -> Element:
        """Create an element"""
        return Element(tag_name)
    
    def create_text_node(self, text: str) -> TextNode:
        """Create a text node"""
        return TextNode(text)
    
    def create_comment(self, text: str) -> CommentNode:
        """Create a comment node"""
        return CommentNode(text)
    
    def get_element_by_id(self, id: str) -> Optional[Element]:
        """Find element by ID"""
        return self.body.get_element_by_id(id)
    
    def query_selector(self, selector: str) -> Optional[Element]:
        """Query selector"""
        return self.body.query_selector(selector)
    
    def query_selector_all(self, selector: str) -> list:
        """Query all matching elements"""
        return self.body.query_selector_all(selector)


# Global document instance
document = Document()


def create_element(tag_name: str) -> Element:
    """Create a DOM element"""
    return document.create_element(tag_name)


def create_text_node(text: str) -> TextNode:
    """Create a text node"""
    return document.create_text_node(text)


def append_child(parent: DOMNode, child: DOMNode) -> DOMNode:
    """Append a child to a parent"""
    return parent.append_child(child)


def remove_child(parent: DOMNode, child: DOMNode) -> DOMNode:
    """Remove a child from a parent"""
    return parent.remove_child(child)


def insert_before(parent: DOMNode, new_node: DOMNode, ref_node: Optional[DOMNode]) -> DOMNode:
    """Insert a node before a reference node"""
    return parent.insert_before(new_node, ref_node)


def set_attribute(element: Element, name: str, value: str) -> None:
    """Set an attribute on an element"""
    element.attributes[name] = value


def remove_attribute(element: Element, name: str) -> None:
    """Remove an attribute from an element"""
    if name in element.attributes:
        del element.attributes[name]


def set_style(element: Element, styles: Dict[str, str]) -> None:
    """Set styles on an element"""
    element.style.update(styles)


def add_event_listener(
    element: Element,
    event_type: str,
    listener: Callable,
    options: Optional[Dict] = None
) -> None:
    """Add an event listener to an element"""
    if event_type not in element._event_listeners:
        element._event_listeners[event_type] = []
    element._event_listeners[event_type].append(listener)


def remove_event_listener(
    element: Element,
    event_type: str,
    listener: Callable
) -> None:
    """Remove an event listener from an element"""
    if event_type in element._event_listeners:
        if listener in element._event_listeners[event_type]:
            element._event_listeners[event_type].remove(listener)


def dispatch_event(element: Element, event_type: str, event_data: Optional[Dict] = None) -> None:
    """Dispatch an event on an element"""
    if event_type in element._event_listeners:
        for listener in element._event_listeners[event_type]:
            listener(event_data or {})
