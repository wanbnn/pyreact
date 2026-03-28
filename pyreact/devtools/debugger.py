"""
Debugger Module
===============

Debugging tools for PyReact components.
"""

from typing import Any, Dict, List, Optional
import time


class Debugger:
    """
    Debugger for PyReact components
    
    Provides tools for inspecting component trees,
    state, props, and lifecycle events.
    
    Example:
        debugger = Debugger()
        debugger.enable()
        
        # Inspect component
        debugger.inspect_component(component)
        
        # Get component tree
        tree = debugger.get_tree()
    """
    
    def __init__(self):
        self._enabled: bool = False
        self._components: Dict[int, Dict] = {}
        self._logs: List[Dict] = []
        self._breakpoints: Dict[str, List[str]] = {}
        self._watch_list: List[str] = []
    
    def enable(self) -> None:
        """Enable debugging"""
        self._enabled = True
    
    def disable(self) -> None:
        """Disable debugging"""
        self._enabled = False
    
    def is_enabled(self) -> bool:
        """Check if debugging is enabled"""
        return self._enabled
    
    def log(self, message: str, data: Optional[Dict] = None) -> None:
        """
        Log a debug message
        
        Args:
            message: Log message
            data: Optional data
        """
        if not self._enabled:
            return
        
        entry = {
            'timestamp': time.time(),
            'message': message,
            'data': data or {}
        }
        self._logs.append(entry)
        
        # Print to console
        print(f"[PyReact Debug] {message}")
        if data:
            print(f"  Data: {data}")
    
    def register_component(self, component: Any) -> None:
        """
        Register a component for debugging
        
        Args:
            component: Component instance
        """
        if not self._enabled:
            return
        
        component_id = id(component)
        self._components[component_id] = {
            'component': component,
            'name': component.__class__.__name__,
            'props': {},
            'state': {},
            'lifecycle_events': [],
            'render_count': 0,
            'created_at': time.time()
        }
        
        self.log(f"Component registered: {component.__class__.__name__}")
    
    def unregister_component(self, component: Any) -> None:
        """
        Unregister a component
        
        Args:
            component: Component instance
        """
        component_id = id(component)
        if component_id in self._components:
            del self._components[component_id]
            self.log(f"Component unregistered: {component.__class__.__name__}")
    
    def update_component_state(
        self,
        component: Any,
        state: Dict[str, Any]
    ) -> None:
        """
        Update component state in debug view
        
        Args:
            component: Component instance
            state: Current state
        """
        if not self._enabled:
            return
        
        component_id = id(component)
        if component_id in self._components:
            self._components[component_id]['state'] = state.copy()
    
    def update_component_props(
        self,
        component: Any,
        props: Dict[str, Any]
    ) -> None:
        """
        Update component props in debug view
        
        Args:
            component: Component instance
            props: Current props
        """
        if not self._enabled:
            return
        
        component_id = id(component)
        if component_id in self._components:
            self._components[component_id]['props'] = props.copy()
    
    def log_lifecycle_event(
        self,
        component: Any,
        event: str,
        data: Optional[Dict] = None
    ) -> None:
        """
        Log a lifecycle event
        
        Args:
            component: Component instance
            event: Event name
            data: Optional data
        """
        if not self._enabled:
            return
        
        component_id = id(component)
        if component_id in self._components:
            self._components[component_id]['lifecycle_events'].append({
                'event': event,
                'timestamp': time.time(),
                'data': data
            })
            
            # Increment render count
            if event == 'render':
                self._components[component_id]['render_count'] += 1
        
        self.log(f"Lifecycle: {component.__class__.__name__}.{event}", data)
    
    def get_component_info(self, component: Any) -> Optional[Dict]:
        """
        Get debug info for a component
        
        Args:
            component: Component instance
        
        Returns:
            dict or None: Component debug info
        """
        component_id = id(component)
        return self._components.get(component_id)
    
    def get_tree(self) -> Dict:
        """
        Get the component tree
        
        Returns:
            dict: Component tree structure
        """
        tree = {'name': 'root', 'children': []}
        
        for info in self._components.values():
            tree['children'].append({
                'name': info['name'],
                'props': info['props'],
                'state': info['state'],
                'render_count': info['render_count']
            })
        
        return tree
    
    def get_logs(self, limit: int = 100) -> List[Dict]:
        """
        Get debug logs
        
        Args:
            limit: Maximum number of logs
        
        Returns:
            list: Recent logs
        """
        return self._logs[-limit:]
    
    def clear_logs(self) -> None:
        """Clear debug logs"""
        self._logs.clear()
    
    def add_breakpoint(self, component_name: str, event: str) -> None:
        """
        Add a breakpoint
        
        Args:
            component_name: Component class name
            event: Event to break on
        """
        if component_name not in self._breakpoints:
            self._breakpoints[component_name] = []
        self._breakpoints[component_name].append(event)
    
    def remove_breakpoint(self, component_name: str, event: str) -> None:
        """
        Remove a breakpoint
        
        Args:
            component_name: Component class name
            event: Event
        """
        if component_name in self._breakpoints:
            if event in self._breakpoints[component_name]:
                self._breakpoints[component_name].remove(event)
    
    def should_break(self, component_name: str, event: str) -> bool:
        """
        Check if should break
        
        Args:
            component_name: Component class name
            event: Event
        
        Returns:
            bool: True if should break
        """
        return (
            component_name in self._breakpoints and
            event in self._breakpoints[component_name]
        )
    
    def watch(self, expression: str) -> None:
        """
        Add expression to watch list
        
        Args:
            expression: Expression to watch
        """
        if expression not in self._watch_list:
            self._watch_list.append(expression)
    
    def unwatch(self, expression: str) -> None:
        """
        Remove expression from watch list
        
        Args:
            expression: Expression to remove
        """
        if expression in self._watch_list:
            self._watch_list.remove(expression)


# Global debugger instance
_debugger = Debugger()


def get_debugger() -> Debugger:
    """Get the global debugger"""
    return _debugger


def debug_component(component: Any) -> Dict:
    """
    Get debug info for a component
    
    Args:
        component: Component instance
    
    Returns:
        dict: Component debug info
    """
    return _debugger.get_component_info(component) or {}


def get_component_tree() -> Dict:
    """
    Get the component tree
    
    Returns:
        dict: Component tree
    """
    return _debugger.get_tree()
