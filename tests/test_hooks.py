"""
Tests for PyReact Hooks Module
"""

import pytest
from pyreact.core.hooks import (
    use_state,
    use_reducer,
    use_effect,
    use_ref,
    use_memo,
    use_callback,
    use_id,
    Ref,
    _deps_changed,
)
from pyreact.core.element import VNode, h


class MockComponent:
    """Mock component for testing hooks"""
    
    def __init__(self):
        self._hooks = []
        self._hook_index = 0
    
    def _schedule_update(self):
        pass


def setup_hooks_context():
    """Setup hooks context for testing"""
    from pyreact.core import hooks
    component = MockComponent()
    hooks._current_component = component
    hooks._hook_index = 0
    return component


class TestUseState:
    """Tests for use_state hook"""
    
    def test_initial_value(self):
        """Test initial value"""
        component = setup_hooks_context()
        value, set_value = use_state(10)
        assert value == 10
    
    def test_functional_initial_value(self):
        """Test functional initial value"""
        component = setup_hooks_context()
        value, set_value = use_state(lambda: 20)
        assert value == 20
    
    def test_set_state(self):
        """Test set_state function"""
        component = setup_hooks_context()
        value, set_value = use_state(0)
        
        set_value(5)
        assert component._hooks[0]['value'] == 5
    
    def test_functional_set_state(self):
        """Test functional set_state"""
        component = setup_hooks_context()
        value, set_value = use_state(0)
        
        set_value(lambda x: x + 1)
        assert component._hooks[0]['value'] == 1


class TestUseReducer:
    """Tests for use_reducer hook"""
    
    def test_initial_state(self):
        """Test initial state"""
        component = setup_hooks_context()
        
        def reducer(state, action):
            return state
        
        state, dispatch = use_reducer(reducer, {'count': 0})
        assert state == {'count': 0}
    
    def test_dispatch(self):
        """Test dispatch function"""
        component = setup_hooks_context()
        
        def reducer(state, action):
            if action['type'] == 'INCREMENT':
                return {'count': state['count'] + 1}
            return state
        
        state, dispatch = use_reducer(reducer, {'count': 0})
        dispatch({'type': 'INCREMENT'})
        
        assert component._hooks[0]['value'] == {'count': 1}
    
    def test_init_function(self):
        """Test init function"""
        component = setup_hooks_context()
        
        def reducer(state, action):
            return state
        
        def init(initial):
            return {'count': initial * 2}
        
        state, dispatch = use_reducer(reducer, 5, init)
        assert state == {'count': 10}


class TestUseEffect:
    """Tests for use_effect hook"""
    
    def test_effect_runs(self):
        """Test that effect runs"""
        component = setup_hooks_context()
        
        called = []
        
        def setup():
            called.append('effect')
            return lambda: called.append('cleanup')
        
        use_effect(setup, [])
        assert 'effect' in called
    
    def test_cleanup_runs(self):
        """Test that cleanup runs"""
        component = setup_hooks_context()
        
        called = []
        
        def setup():
            return lambda: called.append('cleanup')
        
        use_effect(setup, [])
        
        # Simulate re-run with changed deps
        component._hooks[0]['cleanup']()
        assert 'cleanup' in called
    
    def test_deps_change(self):
        """Test that effect runs when deps change"""
        component = setup_hooks_context()
        
        call_count = [0]
        
        def setup():
            call_count[0] += 1
            return lambda: None
        
        # First run
        use_effect(setup, [1])
        assert call_count[0] == 1
        
        # Same deps - should not run
        component._hook_index = 0
        use_effect(setup, [1])
        assert call_count[0] == 1
        
        # Different deps - should run
        component._hook_index = 0
        use_effect(setup, [2])
        assert call_count[0] == 2


class TestUseRef:
    """Tests for use_ref hook"""
    
    def test_initial_value(self):
        """Test initial value"""
        component = setup_hooks_context()
        ref = use_ref('test')
        assert ref.current == 'test'
    
    def test_persist_across_renders(self):
        """Test that ref persists"""
        component = setup_hooks_context()
        ref1 = use_ref('test')
        
        component._hook_index = 0
        ref2 = use_ref('test')
        
        assert ref1 is ref2
    
    def test_mutable(self):
        """Test that ref is mutable"""
        component = setup_hooks_context()
        ref = use_ref(0)
        ref.current = 5
        assert ref.current == 5


class TestUseMemo:
    """Tests for use_memo hook"""
    
    def test_computation(self):
        """Test that computation runs"""
        component = setup_hooks_context()
        
        result = use_memo(lambda: 10 + 5, [])
        assert result == 15
    
    def test_memoization(self):
        """Test that value is memoized"""
        component = setup_hooks_context()
        
        call_count = [0]
        
        def compute():
            call_count[0] += 1
            return 10
        
        result1 = use_memo(compute, [1])
        component._hook_index = 0
        result2 = use_memo(compute, [1])
        
        assert result1 == result2
        assert call_count[0] == 1  # Only computed once
    
    def test_deps_change(self):
        """Test recomputation when deps change"""
        component = setup_hooks_context()
        
        call_count = [0]
        
        def compute():
            call_count[0] += 1
            return 10
        
        use_memo(compute, [1])
        component._hook_index = 0
        use_memo(compute, [2])
        
        assert call_count[0] == 2


class TestUseCallback:
    """Tests for use_callback hook"""
    
    def test_callback_memoization(self):
        """Test that callback is memoized"""
        component = setup_hooks_context()
        
        def my_callback():
            return 'test'
        
        cb1 = use_callback(my_callback, [])
        component._hook_index = 0
        cb2 = use_callback(my_callback, [])
        
        assert cb1 == cb2


class TestUseId:
    """Tests for use_id hook"""
    
    def test_unique_id(self):
        """Test that unique ID is generated"""
        component = setup_hooks_context()
        id1 = use_id()
        assert id1.startswith('pyreact-')
    
    def test_id_persists(self):
        """Test that ID persists across renders"""
        component = setup_hooks_context()
        id1 = use_id()
        component._hook_index = 0
        id2 = use_id()
        assert id1 == id2


class TestRef:
    """Tests for Ref class"""
    
    def test_ref_creation(self):
        """Test Ref creation"""
        ref = Ref()
        assert ref.current is None
    
    def test_ref_value(self):
        """Test Ref value"""
        ref = Ref()
        ref.current = 'test'
        assert ref.current == 'test'
    
    def test_ref_repr(self):
        """Test Ref representation"""
        ref = Ref()
        ref.current = 'test'
        assert 'test' in repr(ref)


class TestDepsChanged:
    """Tests for _deps_changed function"""
    
    def test_no_old_deps(self):
        """Test with no old deps"""
        assert _deps_changed(None, [1]) is True
    
    def test_same_deps(self):
        """Test with same deps"""
        assert _deps_changed([1, 2], [1, 2]) is False
    
    def test_different_deps(self):
        """Test with different deps"""
        assert _deps_changed([1, 2], [1, 3]) is True
    
    def test_different_length(self):
        """Test with different length"""
        assert _deps_changed([1], [1, 2]) is True


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
