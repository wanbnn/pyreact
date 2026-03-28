"""
Diff Utilities Module
=====================

This module provides comparison utilities for props and state.
"""

from typing import Any, Dict, List, Tuple


def diff_objects(old_obj: Dict, new_obj: Dict) -> Tuple[Dict, Dict, List[str]]:
    """
    Compute the difference between two objects
    
    Args:
        old_obj: Original object
        new_obj: New object
    
    Returns:
        tuple: (added_or_changed, removed, changed_keys)
    
    Example:
        added, removed, changed = diff_objects(
            {'a': 1, 'b': 2},
            {'a': 1, 'c': 3}
        )
        # added = {'c': 3}
        # removed = {'b': 2}
        # changed = ['c']
    """
    added_or_changed = {}
    removed = {}
    changed_keys = []
    
    # Find added or changed keys
    for key, value in new_obj.items():
        if key not in old_obj:
            added_or_changed[key] = value
            changed_keys.append(key)
        elif old_obj[key] != value:
            added_or_changed[key] = value
            changed_keys.append(key)
    
    # Find removed keys
    for key in old_obj:
        if key not in new_obj:
            removed[key] = old_obj[key]
    
    return added_or_changed, removed, changed_keys


def shallow_compare(obj1: Any, obj2: Any) -> bool:
    """
    Perform shallow comparison
    
    Args:
        obj1: First object
        obj2: Second object
    
    Returns:
        bool: True if objects are shallowly equal
    """
    if obj1 is obj2:
        return True
    
    if not isinstance(obj1, dict) or not isinstance(obj2, dict):
        return obj1 == obj2
    
    if len(obj1) != len(obj2):
        return False
    
    for key in obj1:
        if key not in obj2 or obj1[key] != obj2[key]:
            return False
    
    return True


def deep_compare(obj1: Any, obj2: Any) -> bool:
    """
    Perform deep comparison
    
    Args:
        obj1: First object
        obj2: Second object
    
    Returns:
        bool: True if objects are deeply equal
    """
    if obj1 is obj2:
        return True
    
    if type(obj1) != type(obj2):
        return False
    
    # Handle primitives
    if not isinstance(obj1, (dict, list, tuple)):
        return obj1 == obj2
    
    # Handle lists/tuples
    if isinstance(obj1, (list, tuple)):
        if len(obj1) != len(obj2):
            return False
        return all(deep_compare(a, b) for a, b in zip(obj1, obj2))
    
    # Handle dicts
    if len(obj1) != len(obj2):
        return False
    
    for key in obj1:
        if key not in obj2:
            return False
        if not deep_compare(obj1[key], obj2[key]):
            return False
    
    return True


def props_changed(
    old_props: Dict[str, Any],
    new_props: Dict[str, Any],
    keys: List[str] = None
) -> bool:
    """
    Check if specific props have changed
    
    Args:
        old_props: Previous props
        new_props: New props
        keys: Specific keys to check (None = all)
    
    Returns:
        bool: True if props changed
    """
    if keys is None:
        return not shallow_compare(old_props, new_props)
    
    for key in keys:
        if old_props.get(key) != new_props.get(key):
            return True
    
    return False


def get_changed_props(
    old_props: Dict[str, Any],
    new_props: Dict[str, Any]
) -> List[str]:
    """
    Get list of changed prop keys
    
    Args:
        old_props: Previous props
        new_props: New props
    
    Returns:
        list: Keys that changed
    """
    changed = []
    
    for key in set(old_props) | set(new_props):
        if old_props.get(key) != new_props.get(key):
            changed.append(key)
    
    return changed


def merge_props(base: Dict, *overrides: Dict) -> Dict:
    """
    Merge multiple props objects
    
    Args:
        base: Base props
        *overrides: Props to merge
    
    Returns:
        dict: Merged props
    """
    result = base.copy()
    for override in overrides:
        result.update(override)
    return result
