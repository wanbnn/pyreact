"""
Object Pool Module
==================

This module provides object pooling for performance optimization.
"""

from typing import Any, Callable, Dict, Generic, List, Optional, TypeVar

T = TypeVar('T')


class ObjectPool(Generic[T]):
    """
    Pool of reusable objects
    
    Reduces garbage collection by reusing objects.
    
    Example:
        pool = ObjectPool(lambda: {'count': 0})
        
        obj = pool.acquire()
        obj['count'] = 5
        # Use object...
        pool.release(obj)
    """
    
    def __init__(
        self,
        factory: Callable[[], T],
        max_size: int = 100,
        reset: Optional[Callable[[T], None]] = None
    ):
        """
        Initialize object pool
        
        Args:
            factory: Function to create new objects
            max_size: Maximum pool size
            reset: Function to reset objects before reuse
        """
        self._factory = factory
        self._max_size = max_size
        self._reset = reset
        self._pool: List[T] = []
        self._in_use: Dict[int, T] = {}
    
    def acquire(self) -> T:
        """
        Acquire an object from the pool
        
        Returns:
            Object from pool or new object
        """
        if self._pool:
            obj = self._pool.pop()
            self._in_use[id(obj)] = obj
            return obj
        
        obj = self._factory()
        self._in_use[id(obj)] = obj
        return obj
    
    def release(self, obj: T) -> None:
        """
        Release an object back to the pool
        
        Args:
            obj: Object to release
        """
        obj_id = id(obj)
        if obj_id not in self._in_use:
            return
        
        del self._in_use[obj_id]
        
        if len(self._pool) < self._max_size:
            if self._reset:
                self._reset(obj)
            self._pool.append(obj)
    
    def clear(self) -> None:
        """Clear the pool"""
        self._pool.clear()
        self._in_use.clear()
    
    def size(self) -> int:
        """Get current pool size"""
        return len(self._pool)
    
    def in_use_count(self) -> int:
        """Get count of objects in use"""
        return len(self._in_use)
    
    def total_count(self) -> int:
        """Get total count of objects"""
        return len(self._pool) + len(self._in_use)


class VNodePool:
    """
    Pool for VNode objects
    
    Optimizes VNode creation for frequent updates.
    """
    
    def __init__(self, max_size: int = 1000):
        self._pool = ObjectPool(
            factory=self._create_vnode,
            max_size=max_size,
            reset=self._reset_vnode
        )
    
    def _create_vnode(self) -> Dict:
        """Create a new VNode dict"""
        return {
            'type': None,
            'props': {},
            'children': [],
            'key': None,
            'ref': None,
            '_dom_node': None,
        }
    
    def _reset_vnode(self, vnode: Dict) -> None:
        """Reset a VNode for reuse"""
        vnode['type'] = None
        vnode['props'] = {}
        vnode['children'] = []
        vnode['key'] = None
        vnode['ref'] = None
        vnode['_dom_node'] = None
    
    def acquire(self) -> Dict:
        """Acquire a VNode from the pool"""
        return self._pool.acquire()
    
    def release(self, vnode: Dict) -> None:
        """Release a VNode back to the pool"""
        self._pool.release(vnode)


class EventPool:
    """
    Pool for synthetic events
    
    Events are pooled and reused for performance.
    """
    
    def __init__(self, max_size: int = 100):
        self._pool = ObjectPool(
            factory=self._create_event,
            max_size=max_size,
            reset=self._reset_event
        )
    
    def _create_event(self) -> Dict:
        """Create a new event dict"""
        return {
            'type': '',
            'target': None,
            'currentTarget': None,
            'nativeEvent': None,
            '_propagation_stopped': False,
            '_default_prevented': False,
        }
    
    def _reset_event(self, event: Dict) -> None:
        """Reset an event for reuse"""
        event['type'] = ''
        event['target'] = None
        event['currentTarget'] = None
        event['nativeEvent'] = None
        event['_propagation_stopped'] = False
        event['_default_prevented'] = False
    
    def acquire(self) -> Dict:
        """Acquire an event from the pool"""
        return self._pool.acquire()
    
    def release(self, event: Dict) -> None:
        """Release an event back to the pool"""
        self._pool.release(event)


# Global pools
_pools: Dict[str, ObjectPool] = {}


def get_pool(name: str) -> Optional[ObjectPool]:
    """
    Get a pool by name
    
    Args:
        name: Pool name
    
    Returns:
        ObjectPool or None
    """
    return _pools.get(name)


def register_pool(name: str, pool: ObjectPool) -> None:
    """
    Register a pool
    
    Args:
        name: Pool name
        pool: ObjectPool instance
    """
    _pools[name] = pool


# Register default pools
register_pool('vnode', VNodePool())
register_pool('event', EventPool())
