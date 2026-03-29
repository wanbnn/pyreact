"""Reconciler Module

This module implements the diff algorithm for comparing VNodes and efficiently updating the DOM.
"""

from typing import Any, Callable, Dict, List, Optional, Union, Set
from .element import VNode
from .component import Component
from ..dom import dom_operations


class Reconciler:
    """
    Reconciler implements the diff algorithm for efficient DOM updates.
    
    The algorithm follows these principles:
    1. Elements of different types → replace completely
    2. Elements of same type → update attributes/props
    3. Children with keys → reorder/move instead of recreate
    4. Components → compare props and decide if re-render needed
    """
    
    def __init__(self):
        self._component_instances: Dict[int, Component] = {}
    
    def diff(
        self,
        old_vnode: Optional[VNode],
        new_vnode: Optional[VNode],
        parent_dom: Any,
        index: int = 0
    ) -> Optional[VNode]:
        """
        Compare two VNodes and apply changes to DOM
        
        Args:
            old_vnode: Previous VNode (or None for new)
            new_vnode: New VNode (or None for removal)
            parent_dom: Parent DOM element
            index: Child index in parent
            
        Returns:
            VNode: The new VNode (may be reused or new)
        """
        # Case 1: New node is None → remove
        if new_vnode is None:
            if old_vnode:
                self._remove_node(parent_dom, old_vnode, index)
            return None
        
        # Case 2: Old node is None → create
        if old_vnode is None:
            new_dom = self.create_dom(new_vnode)
            self._insert_node(parent_dom, new_dom, index)
            return new_vnode
        
        # Case 3: Different types → replace
        if self._get_type(old_vnode) != self._get_type(new_vnode):
            new_dom = self.create_dom(new_vnode)
            self._replace_node(parent_dom, new_dom, old_vnode, index)
            return new_vnode
        
        # Case 4: Same type → update
        if self._is_component(new_vnode):
            return self._update_component(old_vnode, new_vnode)
        else:
            return self._update_dom_element(old_vnode, new_vnode)
    
    def create_dom(self, vnode: VNode) -> Any:
        """
        Create a DOM node from a VNode
        
        Args:
            vnode: Virtual node to create
            
        Returns:
            DOM node
        """
        # Text node
        if isinstance(vnode.type, str) and vnode.type == '#text':
            dom = self._create_text_node(vnode.children[0] if vnode.children else '')
            vnode._dom_node = dom
            return dom
        
        # Component
        if callable(vnode.type) and not isinstance(vnode.type, str):
            return self._create_component_dom(vnode)
        
        # HTML element
        dom = self._create_element(vnode.type)
        vnode._dom_node = dom
        
        # Apply props
        self._apply_props(dom, {}, vnode.props)
        
        # Apply ref
        if vnode.ref:
            vnode.ref.current = dom
        
        # Create children
        for child in vnode.children:
            if isinstance(child, str):
                text_node = self._create_text_node(child)
                dom.append_child(text_node)
            elif isinstance(child, VNode):
                child_dom = self.create_dom(child)
                dom.append_child(child_dom)
        
        return dom
    
    def _create_component_dom(self, vnode: VNode) -> Any:
        """Create DOM for a component"""
        from .hooks import _set_current_component, _reset_hook_index
        
        component_type = vnode.type
        
        # Instantiate component
        if isinstance(component_type, type):
            # Class component
            component = component_type(vnode.props)
        else:
            # Function component - wrap in a simple component
            component = _FunctionComponent(vnode.type, vnode.props)
        
        component._vnode = vnode
        component._hooks = []
        vnode._component_instance = component
        
        # Set component context for hooks
        _set_current_component(component)
        _reset_hook_index()
        
        # Render component
        rendered = component.render()
        
        # Reset context
        _set_current_component(None)
        
        if rendered is None:
            # Render nothing
            return self._create_comment('empty')
        
        dom = self.create_dom(rendered)
        component._dom_node = dom
        vnode._dom_node = dom
        
        # Call lifecycle
        component.component_did_mount()
        
        return dom
    
    def _update_component(self, old_vnode: VNode, new_vnode: VNode) -> VNode:
        """Update a component"""
        from .hooks import _set_current_component, _reset_hook_index
        
        old_component = old_vnode._component_instance
        new_props = new_vnode.props
        
        # Check if should update
        should_update = True
        if hasattr(old_component, 'should_component_update'):
            should_update = old_component.should_component_update(
                new_props, old_component.state
            )
        
        # Update props
        old_component.props = new_props
        new_vnode._component_instance = old_component
        new_vnode._dom_node = old_vnode._dom_node
        
        if should_update:
            # Set component context for hooks
            _set_current_component(old_component)
            _reset_hook_index()
            
            # Re-render
            old_rendered = old_vnode._component_instance._vnode
            new_rendered = old_component.render()
            
            # Reset context
            _set_current_component(None)
            
            if new_rendered is None:
                # Remove
                if old_rendered:
                    self._remove_node(
                        old_vnode._dom_node.parent_node,
                        old_rendered,
                        0
                    )
            else:
                # Diff
                self.diff(old_rendered, new_rendered, old_vnode._dom_node.parent_node)
                old_component._vnode = new_rendered
        
        # Call lifecycle
        if hasattr(old_component, 'component_did_update'):
            old_component.component_did_update(old_vnode.props, old_component.state)
        
        return new_vnode
    
    def _update_dom_element(self, old_vnode: VNode, new_vnode: VNode) -> VNode:
        """Update a DOM element"""
        dom = old_vnode._dom_node
        new_vnode._dom_node = dom
        
        # Update props
        self._apply_props(dom, old_vnode.props, new_vnode.props)
        
        # Update ref
        if new_vnode.ref != old_vnode.ref:
            if old_vnode.ref:
                old_vnode.ref.current = None
            if new_vnode.ref:
                new_vnode.ref.current = dom
        
        # Reconcile children
        self._reconcile_children(old_vnode, new_vnode, dom)
        
        return new_vnode
    
    def _reconcile_children(
        self,
        old_vnode: VNode,
        new_vnode: VNode,
        parent_dom: Any
    ) -> None:
        """
        Reconcile children using keys for minimal DOM operations
        """
        old_children = old_vnode.children
        new_children = new_vnode.children
        
        # Build key map for old children
        old_keyed: Dict[Union[str, int], tuple] = {}
        old_index = 0
        for child in old_children:
            if isinstance(child, VNode) and child.key is not None:
                old_keyed[child.key] = (old_index, child)
            old_index += 1
        
        # Track which old children are used
        used_keys: Set[Union[str, int]] = set()
        
        # Process new children
        new_index = 0
        for new_child in new_children:
            child_key = new_child.key if isinstance(new_child, VNode) else None
            
            if child_key is not None and child_key in old_keyed:
                # Reuse existing child
                old_idx, old_child = old_keyed[child_key]
                used_keys.add(child_key)
                
                # Move if needed
                if old_idx != new_index:
                    self._move_child(parent_dom, old_idx, new_index)
                
                # Diff
                self.diff(old_child, new_child, parent_dom, new_index)
            else:
                # Create new child
                if isinstance(new_child, str):
                    text_node = self._create_text_node(new_child)
                    self._insert_node(parent_dom, text_node, new_index)
                elif isinstance(new_child, VNode):
                    child_dom = self.create_dom(new_child)
                    self._insert_node(parent_dom, child_dom, new_index)
            
            new_index += 1
        
        # Remove unused old children
        for key, (idx, child) in old_keyed.items():
            if key not in used_keys:
                self._remove_node(parent_dom, child, idx)
    
    def unmount(self, vnode: VNode) -> None:
        """
        Unmount a VNode and its children
        
        Args:
            vnode: VNode to unmount
        """
        if vnode._component_instance:
            component = vnode._component_instance
            component.component_will_unmount()
        
        # Unmount children
        for child in vnode.children:
            if isinstance(child, VNode):
                self.unmount(child)
        
        # Clear ref
        if vnode.ref:
            vnode.ref.current = None
    
    # DOM Operations - using dom_operations module
    
    def _create_element(self, tag: str) -> Any:
        """Create a DOM element"""
        return dom_operations.create_element(tag)
    
    def _create_text_node(self, text: str) -> Any:
        """Create a text node"""
        return dom_operations.create_text_node(text)
    
    def _create_comment(self, text: str) -> Any:
        """Create a comment node"""
        # For now, use a text node as fallback
        return dom_operations.create_text_node(f'<!-- {text} -->')
    
    def _apply_props(self, dom: Any, old_props: Dict, new_props: Dict) -> None:
        """Apply props to DOM element"""
        # Remove old props
        for key in old_props:
            if key not in new_props:
                self._remove_prop(dom, key, old_props[key])
        
        # Set new props
        for key, value in new_props.items():
            if old_props.get(key) != value:
                self._set_prop(dom, key, value)
    
    def _set_prop(self, dom: Any, key: str, value: Any) -> None:
        """Set a single prop on DOM element"""
        if key == 'className':
            dom.set_attribute('class', value)
        elif key == 'style' and isinstance(value, dict):
            for style_key, style_value in value.items():
                dom.set_style(style_key, style_value)
        elif key.startswith('on'):
            # Event handler
            event_name = key[2:].lower()
            dom.add_event_listener(event_name, value)
        elif key == 'dangerouslySetInnerHTML':
            dom.set_inner_html(value.get('__html', ''))
        else:
            dom.set_attribute(key, value)
    
    def _remove_prop(self, dom: Any, key: str, value: Any) -> None:
        """Remove a prop from DOM element"""
        if key == 'className':
            dom.remove_attribute('class')
        elif key == 'style':
            dom.remove_attribute('style')
        elif key.startswith('on'):
            event_name = key[2:].lower()
            dom.remove_event_listener(event_name)
        else:
            dom.remove_attribute(key)
    
    def _insert_node(self, parent: Any, node: Any, index: int) -> None:
        """Insert node at index"""
        parent.insert_child(node, index)
    
    def _remove_node(self, parent: Any, vnode: VNode, index: int) -> None:
        """Remove node at index"""
        parent.remove_child_at(index)
        self.unmount(vnode)
    
    def _replace_node(self, parent: Any, new_node: Any, old_vnode: VNode, index: int) -> None:
        """Replace node at index"""
        self.unmount(old_vnode)
        parent.replace_child_at(new_node, index)
    
    def _move_child(self, parent: Any, old_index: int, new_index: int) -> None:
        """Move child from old_index to new_index"""
        parent.move_child(old_index, new_index)
    
    def _get_type(self, vnode: VNode) -> Any:
        """Get the type of a VNode for comparison"""
        return vnode.type
    
    def _is_component(self, vnode: VNode) -> bool:
        """Check if VNode is a component"""
        return callable(vnode.type) and not isinstance(vnode.type, str)


class _FunctionComponent:
    """Wrapper for function components"""
    
    def __init__(self, render_fn: Callable, props: Dict):
        self.render_fn = render_fn
        self.props = props
        self.state = {}
        self._vnode = None
        self._dom_node = None
    
    def render(self) -> Optional[VNode]:
        return self.render_fn(self.props)
    
    def component_did_mount(self) -> None:
        pass
    
    def component_will_unmount(self) -> None:
        pass
    
    def should_component_update(self, next_props, next_state) -> bool:
        return self.props != next_props
