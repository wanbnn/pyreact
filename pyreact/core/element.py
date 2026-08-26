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
    # Flatten positional children (handle nested lists). Positional children
    # intentionally take precedence over an explicit component ``children`` prop,
    # matching createElement-style composition semantics.
    flat_children: List[Union[VNode, str]] = []
    for child in children:
        if isinstance(child, (list, tuple)):
            flat_children.extend(_flatten_children(child))
        elif isinstance(child, bool) or child is None:
            continue
        elif isinstance(child, (int, float)):
            flat_children.append(str(child))
        elif isinstance(child, (VNode, str)) or callable(child):
            flat_children.append(child)
        else:
            # Portals and other renderer extensions are accepted explicitly.
            from .portal import is_portal
            if is_portal(child):
                flat_children.append(child)
            else:
                raise TypeError(f'Unsupported child type: {child.__class__.__name__}')

    # Extract special props. Component children are also exposed through props,
    # which is the contract documented by PyReact and expected by composition
    # APIs such as Context and ErrorBoundary.
    props = props.copy() if props else {}
    key = props.pop('key', None)
    ref = props.pop('ref', None)
    if callable(type) and not isinstance(type, str):
        if not children and 'children' in props:
            flat_children = _flatten_children([props['children']])
        props['children'] = flat_children
    
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
        if isinstance(child, (list, tuple)):
            result.extend(_flatten_children(child))
        elif isinstance(child, bool) or child is None:
            continue
        elif isinstance(child, (int, float)):
            result.append(str(child))
        elif isinstance(child, (VNode, str)) or callable(child):
            result.append(child)
        else:
            from .portal import is_portal
            if is_portal(child):
                result.append(child)
            else:
                raise TypeError(f'Unsupported child type: {child.__class__.__name__}')
    return result


def create_element(
    type: Union[str, Callable, type],
    props: Optional[Dict[str, Any]] = None,
    *children: Union['VNode', str, List[Union['VNode', str]]]
) -> VNode:
    """
    Alias for h() function
    
    Provided for compatibility with React's createElement API.
    
    Args:
        type: Element type
        props: Properties/attributes (optional)
        *children: Child elements (VNodes, strings, or lists)
    
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
        bool: True if value is a valid VNode
    """
    return isinstance(element, VNode)


def clone_element(
    element: VNode,
    props: Optional[Dict[str, Any]] = None,
    *children: Union['VNode', str, List[Union['VNode', str]]]
) -> VNode:
    """
    Clone an existing VNode with optional prop/child overrides.

    Positional children override both the original children and an explicit
    ``children`` prop. When no positional children are supplied, an explicit
    ``children`` prop is normalized and becomes the cloned VNode children.
    """
    if not is_valid_element(element):
        raise ValueError('clone_element expects a valid VNode')

    new_props = element.props.copy()
    explicit_children = props is not None and 'children' in props
    if props:
        new_props.update(props)

    if children:
        new_children = _flatten_children(list(children))
    elif explicit_children:
        new_children = _flatten_children([new_props.get('children')])
    else:
        new_children = element.children.copy()

    if callable(element.type) and not isinstance(element.type, str):
        new_props['children'] = new_children

    key = new_props.pop('key', element.key)
    ref = new_props.pop('ref', element.ref)

    return VNode(
        type=element.type,
        props=new_props,
        children=new_children,
        key=key,
        ref=ref,
    )
