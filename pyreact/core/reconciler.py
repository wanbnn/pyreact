"""Reconciler Module

This module implements the diff algorithm for comparing VNodes and efficiently updating the DOM.
"""

from typing import Any, Callable, Dict, List, Optional
import warnings
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
        self._detached_updates: List[Any] = []
        self._component_counter = 0

    def _assign_component_id(self, component: Any) -> None:
        component._tree_id = self._component_counter
        self._component_counter += 1

    def flush_detached_updates(self) -> None:
        pending = self._detached_updates.copy()
        self._detached_updates.clear()
        for component in pending:
            self._rerender_component(component)

    @staticmethod
    def _normalize_component_output(rendered: Any) -> Optional[VNode]:
        """Normalize the single-root component contract."""
        if rendered is None or isinstance(rendered, VNode):
            return rendered
        if isinstance(rendered, list):
            if not rendered:
                return None
            if len(rendered) == 1 and isinstance(rendered[0], VNode):
                return rendered[0]
            raise TypeError('Components must return one VNode; wrap multiple children in an element')
        raise TypeError(f'Components must return VNode or None, got {type(rendered).__name__}')

    @staticmethod
    def _component_render(component: Any) -> Optional[VNode]:
        from .hooks import _set_current_component, _reset_hook_index
        from ..devtools.debugger import get_debugger
        from ..devtools.profiler import get_profiler

        name = getattr(
            getattr(component, 'render_fn', None), '__name__', component.__class__.__name__
        )
        profiler = get_profiler()
        debugger = get_debugger()
        profiler.begin_render(name)
        debugger.log_lifecycle_event(component, 'render')
        _set_current_component(component)
        _reset_hook_index()
        component._is_rendering = True
        try:
            rendered = Reconciler._normalize_component_output(component.render())
            if getattr(component, '_is_mounted', False) and component._hook_index != len(
                component._hooks
            ):
                raise RuntimeError('Hook count changed between renders')
            return rendered
        finally:
            component._is_rendering = False
            _set_current_component(None)
            profiler.end_render(name)

    @staticmethod
    def _flush_effects(component: Any, layout: bool) -> None:
        """Commit pending effect hooks after the DOM mutation phase."""
        for hook in getattr(component, '_hooks', []):
            if hook.get('type') != 'effect' or not hook.get('pending'):
                continue
            if bool(hook.get('layout')) != layout:
                continue
            cleanup = hook.get('cleanup')
            if cleanup:
                try:
                    cleanup()
                except Exception as error:
                    warnings.warn(f'Effect cleanup failed: {error}', RuntimeWarning)
            setup = hook.get('setup')
            hook['cleanup'] = setup() if setup else None
            hook['pending'] = False
    
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
        from .portal import is_portal

        # Portals render outside the parent tree and keep only a placeholder here.
        if old_vnode is not None and new_vnode is not None and (
            is_portal(old_vnode) or is_portal(new_vnode)
        ):
            new_dom = self.create_dom(new_vnode)
            self._replace_node(parent_dom, new_dom, old_vnode, index)
            return new_vnode

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
        from .portal import is_portal, render_portal
        if is_portal(vnode):
            render_portal(vnode, self)
            placeholder = self._create_comment('portal')
            vnode._placeholder = placeholder
            return placeholder

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
            from .refs import attach_ref
            attach_ref(vnode.ref, dom)
        
        # Create children
        for child in vnode.children:
            if isinstance(child, str):
                text_node = self._create_text_node(child)
                dom.append_child(text_node)
            elif isinstance(child, VNode):
                child_dom = self.create_dom(child)
                dom.append_child(child_dom)
            elif is_portal(child):
                dom.append_child(self.create_dom(child))
        
        return dom

    def hydrate_dom(self, vnode: VNode, dom: Any, path: str = 'root') -> Any:
        """Attach a VNode tree to existing DOM without recreating its nodes."""
        from ..server.hydration import HydrationMismatchError

        if callable(vnode.type) and not isinstance(vnode.type, str):
            component_type = vnode.type
            component_props = vnode.props
            if getattr(component_type, '_forward_ref', False):
                component_props = {**component_props, 'ref': vnode.ref}
            component = component_type(component_props) if isinstance(
                component_type, type
            ) else _FunctionComponent(component_type, component_props)
            component._hooks = []
            component._hook_index = 0
            self._assign_component_id(component)
            component._owner_vnode = vnode
            component._updater = lambda instance: self._rerender_component(instance)
            vnode._component_instance = component

            provider_context = getattr(component_type, '_pyreact_context_provider', None)
            provider_id = id(component)
            if provider_context is not None:
                provider_context._push_provider(
                    provider_id, component.props.get('value', provider_context._default_value)
                )
            try:
                rendered = self._component_render(component)
                if rendered is None:
                    if getattr(dom, 'node_type', None) != 'text':
                        raise HydrationMismatchError(f'Expected empty placeholder at {path}')
                else:
                    self.hydrate_dom(rendered, dom, f'{path}/{getattr(rendered, "type", "node")}')
            finally:
                if provider_context is not None:
                    provider_context._pop_provider(provider_id)

            component._vnode = rendered
            component._dom_node = dom
            component._is_mounted = True
            vnode._dom_node = dom
            self._flush_effects(component, layout=True)
            if hasattr(component, 'component_did_mount'):
                component.component_did_mount()
            self._flush_effects(component, layout=False)
            return dom

        if vnode.type == '#text':
            expected = vnode.children[0] if vnode.children else ''
            if getattr(dom, 'node_type', None) != 'text' or dom.text_content != expected:
                raise HydrationMismatchError(f'Text mismatch at {path}')
            vnode._dom_node = dom
            return dom

        if getattr(dom, 'node_type', None) != 'element':
            raise HydrationMismatchError(f'Expected element <{vnode.type}> at {path}')
        if getattr(dom, 'tag_name', '').lower() != str(vnode.type).lower():
            raise HydrationMismatchError(
                f'Tag mismatch at {path}: server={getattr(dom, "tag_name", None)}, '
                f'client={vnode.type}'
            )

        vnode._dom_node = dom
        self._apply_props(dom, {}, vnode.props)
        if vnode.ref:
            from .refs import attach_ref
            attach_ref(vnode.ref, dom)

        if 'dangerouslySetInnerHTML' in vnode.props:
            return dom
        if len(dom.child_nodes) != len(vnode.children):
            raise HydrationMismatchError(
                f'Child count mismatch at {path}: server={len(dom.child_nodes)}, '
                f'client={len(vnode.children)}'
            )
        for index, child in enumerate(vnode.children):
            child_dom = dom.child_nodes[index]
            child_path = f'{path}/{index}'
            if isinstance(child, str):
                if getattr(child_dom, 'node_type', None) != 'text' or child_dom.text_content != child:
                    raise HydrationMismatchError(f'Text mismatch at {child_path}')
            else:
                self.hydrate_dom(child, child_dom, child_path)
        return dom
    
    def _create_component_dom(self, vnode: VNode) -> Any:
        """Create DOM for a component"""
        component_type = vnode.type
        component_props = vnode.props
        if getattr(component_type, '_forward_ref', False):
            component_props = {**component_props, 'ref': vnode.ref}
        
        # Instantiate component
        if isinstance(component_type, type):
            # Class component
            component = component_type(component_props)
        else:
            # Function component - wrap in a simple component
            component = _FunctionComponent(vnode.type, component_props)

        if isinstance(component, Component):
            derived = component.get_derived_state_from_props(component.props, component.state)
            if derived:
                component.state = {**component.state, **derived}
            component.component_will_mount()
        
        component._hooks = []
        component._hook_index = 0
        self._assign_component_id(component)
        component._is_rendering = False
        component._owner_vnode = vnode
        vnode._component_instance = component
        
        provider_context = getattr(component_type, '_pyreact_context_provider', None)
        provider_id = id(component)
        if provider_context is not None:
            provider_context._push_provider(
                provider_id, component.props.get('value', provider_context._default_value)
            )
        try:
            rendered = self._component_render(component)
        
            if rendered is None:
                # Render nothing
                dom = self._create_comment('empty')
                component._vnode = None
            else:
                try:
                    dom = self.create_dom(rendered)
                except Exception as error:
                    derived = component.get_derived_state_from_error(error) if hasattr(
                        component, 'get_derived_state_from_error'
                    ) else None
                    if derived is None:
                        raise
                    component.state = {**component.state, **derived}
                    if hasattr(component, 'component_did_catch'):
                        component.component_did_catch(error, {'componentStack': repr(rendered)})
                    rendered = self._component_render(component)
                    if rendered is None:
                        dom = self._create_comment('empty')
                    else:
                        dom = self.create_dom(rendered)
                component._vnode = rendered
        finally:
            if provider_context is not None:
                provider_context._pop_provider(provider_id)
        
        component._dom_node = dom
        component._updater = lambda instance: self._rerender_component(instance)
        component._is_mounted = True
        vnode._dom_node = dom
        
        # Call lifecycle
        self._flush_effects(component, layout=True)
        from ..devtools.debugger import get_debugger
        debugger = get_debugger()
        debugger.register_component(component)
        debugger.update_component_props(component, component.props)
        debugger.update_component_state(component, component.state)
        if hasattr(component, 'component_did_mount'):
            component.component_did_mount()
        debugger.log_lifecycle_event(component, 'mount')
        self._flush_effects(component, layout=False)
        
        return dom

    def _rerender_component(self, component: Any) -> None:
        """Commit state/hook updates for an already mounted component."""
        old_rendered = component._vnode
        old_dom = component._dom_node
        parent = old_dom.parent_node if old_dom is not None else None
        if parent is None:
            component._apply_state() if hasattr(component, '_apply_state') else None
            if component not in self._detached_updates:
                self._detached_updates.append(component)
            return

        prev_props = component.props.copy()
        prev_state = component.state.copy()
        next_state = getattr(component, '_pending_state', None) or component.state
        derived = component.get_derived_state_from_props(component.props, next_state) if isinstance(
            component, Component
        ) else None
        if derived:
            next_state = {**next_state, **derived}
            component._pending_state = next_state
        should_update = isinstance(component, _FunctionComponent) or bool(
            getattr(component, '_force_update', False)
        )
        if hasattr(component, 'should_component_update') and not isinstance(
            component, _FunctionComponent
        ) and not should_update:
            should_update = component.should_component_update(component.props, next_state)

        if should_update and isinstance(component, Component):
            component.component_will_update(component.props, next_state)

        if hasattr(component, '_apply_state'):
            component._apply_state()
        component._force_update = False

        if should_update:
            new_rendered = self._component_render(component)

            index = parent.child_nodes.index(old_dom)
            new_dom = old_dom
            if old_rendered is None and new_rendered is None:
                pass
            elif old_rendered is None:
                new_dom = self.create_dom(new_rendered)
                parent.replace_child_at(new_dom, index)
            elif new_rendered is None:
                new_dom = self._create_comment('empty')
                parent.replace_child_at(new_dom, index)
            else:
                self.diff(old_rendered, new_rendered, parent, index)
                new_dom = new_rendered._dom_node

            component._vnode = new_rendered
            component._dom_node = new_dom
            component._owner_vnode._dom_node = component._dom_node

            self._flush_effects(component, layout=True)
            if hasattr(component, 'component_did_update'):
                component.component_did_update(prev_props, prev_state)
            self._flush_effects(component, layout=False)

        if hasattr(component, '_run_callbacks'):
            component._run_callbacks()
    
    def _update_component(self, old_vnode: VNode, new_vnode: VNode) -> VNode:
        """Update a component"""
        old_component = old_vnode._component_instance
        if old_component is None:
            raise RuntimeError('Cannot update an unmounted component')
        new_props = new_vnode.props
        if getattr(new_vnode.type, '_forward_ref', False):
            new_props = {**new_props, 'ref': new_vnode.ref}
        prev_props = old_component.props.copy()
        prev_state = old_component.state.copy()

        if isinstance(old_component, Component):
            old_component.component_will_receive_props(new_props)
            derived = old_component.get_derived_state_from_props(new_props, old_component.state)
            if derived:
                old_component.state = {**old_component.state, **derived}
        
        # Check if should update
        should_update = bool(getattr(old_component, '_force_update', False))
        if hasattr(old_component, 'should_component_update') and not should_update:
            should_update = old_component.should_component_update(
                new_props, old_component.state
            )
        if should_update and isinstance(old_component, Component):
            old_component.component_will_update(new_props, old_component.state)
        old_component._force_update = False
        
        # Update props and preserve the mounted instance.
        old_component.props = new_props
        old_component._owner_vnode = new_vnode
        new_vnode._component_instance = old_component
        new_vnode._dom_node = old_vnode._dom_node
        
        if should_update:
            old_rendered = old_component._vnode
            new_rendered = self._component_render(old_component)
            parent = old_vnode._dom_node.parent_node
            index = parent.child_nodes.index(old_vnode._dom_node)
            if old_rendered is None and new_rendered is None:
                new_dom = old_vnode._dom_node
            elif old_rendered is None:
                new_dom = self.create_dom(new_rendered)
                parent.replace_child_at(new_dom, index)
            elif new_rendered is None:
                new_dom = self._create_comment('empty')
                self.unmount(old_rendered)
                parent.replace_child_at(new_dom, index)
            else:
                self.diff(old_rendered, new_rendered, parent, index)
                new_dom = new_rendered._dom_node
            old_component._vnode = new_rendered
            old_component._dom_node = new_dom
            new_vnode._dom_node = new_dom
            self._flush_effects(old_component, layout=True)
            from ..devtools.debugger import get_debugger
            debugger = get_debugger()
            debugger.update_component_props(old_component, old_component.props)
            debugger.update_component_state(old_component, old_component.state)
            if hasattr(old_component, 'component_did_update'):
                old_component.component_did_update(prev_props, prev_state)
            debugger.log_lifecycle_event(old_component, 'update')
            self._flush_effects(old_component, layout=False)
        
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
                from .refs import detach_ref
                detach_ref(old_vnode.ref)
            if new_vnode.ref:
                from .refs import attach_ref
                attach_ref(new_vnode.ref, dom)
        
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
        working = list(old_vnode.children)

        def same_identity(old_child: Any, new_child: Any, position: int) -> bool:
            if isinstance(new_child, VNode) and new_child.key is not None:
                return isinstance(old_child, VNode) and old_child.key == new_child.key
            return position < len(working) and old_child is working[position]

        for index, new_child in enumerate(new_vnode.children):
            match_index: Optional[int] = None
            if isinstance(new_child, VNode) and new_child.key is not None:
                for candidate_index, candidate in enumerate(working):
                    if same_identity(candidate, new_child, candidate_index):
                        match_index = candidate_index
                        break
            elif index < len(working):
                match_index = index

            if match_index is None:
                new_dom = self._create_text_node(new_child) if isinstance(
                    new_child, str
                ) else self.create_dom(new_child)
                self._insert_node(parent_dom, new_dom, index)
                working.insert(index, new_child)
                continue

            if match_index != index:
                self._move_child(parent_dom, match_index, index)
                working.insert(index, working.pop(match_index))

            old_child = working[index]
            if isinstance(old_child, str) and isinstance(new_child, str):
                if old_child != new_child:
                    parent_dom.child_nodes[index].text_content = new_child
            elif isinstance(old_child, VNode) and isinstance(new_child, VNode):
                self.diff(old_child, new_child, parent_dom, index)
            else:
                new_dom = self._create_text_node(new_child) if isinstance(
                    new_child, str
                ) else self.create_dom(new_child)
                parent_dom.replace_child_at(new_dom, index)
                if isinstance(old_child, VNode):
                    self.unmount(old_child)
            working[index] = new_child

        for index in range(len(working) - 1, len(new_vnode.children) - 1, -1):
            old_child = working[index]
            parent_dom.remove_child_at(index)
            if isinstance(old_child, VNode):
                self.unmount(old_child)
    
    def unmount(self, vnode: VNode) -> None:
        """
        Unmount a VNode and its children
        
        Args:
            vnode: VNode to unmount
        """
        from .portal import is_portal, unmount_portal
        if is_portal(vnode):
            unmount_portal(vnode)
            return
        if vnode._component_instance:
            component = vnode._component_instance
            if hasattr(component, 'component_will_unmount'):
                component.component_will_unmount()
            from ..devtools.debugger import get_debugger
            get_debugger().unregister_component(component)
            for hook in getattr(component, '_hooks', []):
                if hook.get('type') == 'effect' and hook.get('cleanup'):
                    try:
                        hook['cleanup']()
                    except Exception as error:
                        warnings.warn(f'Effect cleanup failed: {error}', RuntimeWarning)
                    hook['cleanup'] = None
            if component._vnode:
                self.unmount(component._vnode)
        
        # Unmount children
        for child in vnode.children:
            if isinstance(child, VNode) or is_portal(child):
                self.unmount(child)
        
        # Clear ref
        if vnode.ref:
            from .refs import detach_ref
            detach_ref(vnode.ref)
    
    # DOM Operations - using dom_operations module
    
    def _create_element(self, tag: str) -> Any:
        """Create a DOM element"""
        return dom_operations.create_element(tag)
    
    def _create_text_node(self, text: str) -> Any:
        """Create a text node"""
        return dom_operations.create_text_node(text)
    
    def _create_comment(self, text: str) -> Any:
        """Create a comment node"""
        return dom_operations.document.create_comment(text)
    
    def _apply_props(self, dom: Any, old_props: Dict, new_props: Dict) -> None:
        """Apply props to DOM element"""
        # Remove old props
        for key in old_props:
            if key not in new_props:
                self._remove_prop(dom, key, old_props[key])
        
        # Set new props
        for key, value in new_props.items():
            if old_props.get(key) != value:
                if key == 'style' and isinstance(old_props.get(key), dict) and isinstance(value, dict):
                    for style_key in old_props[key]:
                        if style_key not in value:
                            dom.style.pop(style_key, None)
                if key.startswith('on') and key in old_props:
                    self._remove_prop(dom, key, old_props[key])
                self._set_prop(dom, key, value)
    
    def _set_prop(self, dom: Any, key: str, value: Any) -> None:
        """Set a single prop on DOM element"""
        from ..dom.attributes import get_attribute_name, is_boolean_attribute

        if key == 'className':
            dom.set_attribute('class', value)
        elif key == 'style' and isinstance(value, dict):
            for style_key, style_value in value.items():
                if style_value is None:
                    dom.style.pop(style_key, None)
                else:
                    dom.set_style(style_key, style_value)
        elif key.startswith('on'):
            # Event handler
            event_name = key[2:].lower()
            dom.add_event_listener(event_name, value)
        elif key == 'dangerouslySetInnerHTML':
            if not isinstance(value, dict) or '__html' not in value:
                raise ValueError('dangerouslySetInnerHTML requires a {"__html": value} mapping')
            dom.set_inner_html(value.get('__html', ''))
        elif key == 'children' or key == 'suppressHydrationWarning':
            return
        else:
            name = get_attribute_name(key)
            if value is None or value is False:
                dom.remove_attribute(name)
            elif value is True and is_boolean_attribute(name):
                dom.set_attribute(name, True)
            else:
                dom.set_attribute(name, value)
    
    def _remove_prop(self, dom: Any, key: str, value: Any) -> None:
        """Remove a prop from DOM element"""
        if key == 'className':
            dom.remove_attribute('class')
        elif key == 'style':
            dom.style.clear()
        elif key.startswith('on'):
            event_name = key[2:].lower()
            dom.remove_event_listener(event_name)
        elif key == 'dangerouslySetInnerHTML':
            dom._raw_inner_html = False
            dom._text_content = ''
        elif key not in ('children', 'suppressHydrationWarning'):
            from ..dom.attributes import get_attribute_name
            dom.remove_attribute(get_attribute_name(key))
    
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
        from .portal import is_portal
        return type(vnode) if is_portal(vnode) else vnode.type
    
    def _is_component(self, vnode: VNode) -> bool:
        """Check if VNode is a component"""
        vnode_type = getattr(vnode, 'type', None)
        return callable(vnode_type) and not isinstance(vnode_type, str)


class _FunctionComponent:
    """Wrapper for function components"""
    
    def __init__(self, render_fn: Callable, props: Dict):
        self.render_fn = render_fn
        self.props = props
        self.state = {}
        self._vnode = None
        self._dom_node = None
        self._updater = None
        self._hooks = []
        self._hook_index = 0
        self._is_rendering = False
    
    def render(self) -> Optional[VNode]:
        return self.render_fn(self.props)

    def _schedule_update(self) -> None:
        if self._updater:
            self._updater(self)
    
    def component_did_mount(self) -> None:
        pass
    
    def component_will_unmount(self) -> None:
        pass
    
    def should_component_update(self, next_props, next_state) -> bool:
        compare = getattr(self.render_fn, '_pyreact_memo_compare', None)
        return not compare(self.props, next_props) if compare else self.props != next_props
