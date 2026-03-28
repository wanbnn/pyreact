"""
Virtual DOM Element Module
==========================

This module defines VNode (Virtual Node) and the h() function (hyperscript)
for creating virtual DOM elements in PyReact.
"""

from typing import Any, Callable, Dict, List, Optional, Union, TYPE_CHECKING

if TYPE_CHECKING:
    from .component import Component


class VNode:
    """
    Virtual DOM Node
    
    Represents a node in the virtual DOM tree. Can be:
    - An HTML element ('div', 'span', etc.)
    - A Component (function or class)
    - A text node (string)
    
    Attributes:
        type: Element type (string tag name or Component class/callable)
        props: Dictionary of properties/attributes
        children: List of child VNodes or strings
        key: Optional key for list reconciliation
        ref: Optional reference to DOM node or component instance
    """
    
    def __init__(
        self,
        type: Union[str, Callable, type],
        props: Optional[Dict[str, Any]] = None,
        children: Optional[List[Union['VNode', str]]] = None,
        key: Optional[Union[str, int]] = None,
        ref: Optional[Any] = None
    ):
        self.type = type
        self.props = props or {}
        self.children = children or []
        self.key = key
        self.ref = ref
        
        # Internal properties (managed by renderer)
        self._dom_node: Optional[Any] = None
        self._parent: Optional['VNode'] = None
        self._component_instance: Optional['Component'] = None
        self._hooks: List[Any] = []
        self._hook_index: int = 0
    
    def __repr__(self) -> str:
        type_name = self.type if isinstance(self.type, str) else self.type.__name__
        return f"VNode(type={type_name!r}, key={self.key!r}, children={len(self.children)})"
    
    def __eq__(self, other: Any) -> bool:
        if not isinstance(other, VNode):
            return False
        return (
            self.type == other.type and
            self.key == other.key and
            self.props == other.props
        )
    
    def clone(self) -> 'VNode':
        """Create a shallow clone of this VNode"""
        return VNode(
            type=self.type,
            props=self.props.copy(),
            children=self.children.copy(),
            key=self.key,
            ref=self.ref
        )


def h(
    type: Union[str, Callable, type],
    props: Optional[Dict[str, Any]] = None,
    *children: Union['VNode', str, List[Union['VNode', str]]]
) -> VNode:
    """
    Create a virtual DOM element (hyperscript function)
    
    This is the primary way to create VNodes in PyReact, similar to
    React.createElement().
    
    Args:
        type: Element type - HTML tag string ('div', 'span') or Component
        props: Dictionary of properties/attributes (optional)
        *children: Child elements (VNodes, strings, or lists)
    
    Returns:
        VNode: The created virtual node
    
    Examples:
        >>> h('div', {'id': 'app'}, 'Hello World')
        VNode(type='div', key=None, children=1)
        
        >>> h('div', None, h('span', None, 'text'))
        VNode(type='div', key=None, children=1)
        
        >>> h(Counter, {'initialCount': 0})
        VNode(type='Counter', key=None, children=0)
    """
    # Flatten children (handle nested lists)
    flat_children: List[Union[VNode, str]] = []
    for child in children:
        if isinstance(child, list):
            flat_children.extend(_flatten_children(child))
        elif child is not None:
            flat_children.append(child)
    
    # Extract special props
    props = props.copy() if props else {}
    key = props.pop('key', None)
    ref = props.pop('ref', None)
    
    return VNode(
        type=type,
        props=props,
        children=flat_children,
        key=key,
        ref=ref
    )


def _flatten_children(
    children: List[Union[VNode, str, List]]
) -> List[Union[VNode, str]]:
    """Recursively flatten nested children lists"""
    result: List[Union[VNode, str]] = []
    for child in children:
        if isinstance(child, list):
            result.extend(_flatten_children(child))
        elif child is not None:
            result.append(child)
    return result


def create_element(
    type: Union[str, Callable, type],
    props: Optional[Dict[str, Any]] = None,
    *children: Union[VNode, str, List[Union[VNode, str]]]
) -> VNode:
    """
    Alias for h() function
    
    Provided for compatibility with React's createElement API.
    
    Args:
        type: Element type
        props: Properties/attributes
        *children: Child elements
    
    Returns:
        VNode: The created virtual node
    """
    return h(type, props, *children)


def is_valid_element(element: Any) -> bool:
    """
    Check if a value is a valid VNode
    
    Args:
        element: Value to check
    
    Returns:
        bool: True if element is a valid VNode
    """
    return isinstance(element, VNode)


def clone_element(
    element: VNode,
    props: Optional[Dict[str, Any]] = None,
    *children: Union[VNode, str, List[Union[VNode, str]]]
) -> VNode:
    """
    Clone and return a new VNode with optional new props and children
    
    Args:
        element: VNode to clone
        props: New props to merge (optional)
        *children: New children (optional)
    
    Returns:
        VNode: Cloned element
    """
    if not is_valid_element(element):
        raise ValueError('clone_element requires a valid VNode')
    
    # Merge props
    new_props = element.props.copy()
    if props:
        new_props.update(props)
    
    # Use new children if provided, otherwise keep original
    new_children = list(children) if children else element.children.copy()
    
    return VNode(
        type=element.type,
        props=new_props,
        children=new_children,
        key=props.get('key', element.key) if props else element.key,
        ref=props.get('ref', element.ref) if props else element.ref
    )
