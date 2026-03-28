"""
Tests for PyReact Core Module
"""

import pytest
from pyreact.core.element import VNode, h, create_element, is_valid_element, clone_element
from pyreact.core.component import Component, PureComponent, shallow_equal


class TestVNode:
    """Tests for VNode class"""
    
    def test_vnode_creation(self):
        """Test basic VNode creation"""
        vnode = VNode('div', {'className': 'test'}, [])
        assert vnode.type == 'div'
        assert vnode.props == {'className': 'test'}
        assert vnode.children == []
    
    def test_vnode_with_children(self):
        """Test VNode with children"""
        child = VNode('span', {}, [])
        parent = VNode('div', {}, [child])
        assert len(parent.children) == 1
        assert parent.children[0] == child
    
    def test_vnode_repr(self):
        """Test VNode string representation"""
        vnode = VNode('div', {}, [])
        assert 'div' in repr(vnode)
    
    def test_vnode_equality(self):
        """Test VNode equality"""
        vnode1 = VNode('div', {'id': 'test'}, [])
        vnode2 = VNode('div', {'id': 'test'}, [])
        vnode3 = VNode('span', {'id': 'test'}, [])
        
        assert vnode1 == vnode2
        assert vnode1 != vnode3
    
    def test_vnode_clone(self):
        """Test VNode cloning"""
        original = VNode('div', {'className': 'test'}, [])
        cloned = original.clone()
        
        assert original.type == cloned.type
        assert original.props == cloned.props
        assert original is not cloned


class TestHFunction:
    """Tests for h() function"""
    
    def test_h_basic_element(self):
        """Test creating basic element"""
        vnode = h('div', {'id': 'test'}, 'Hello')
        assert vnode.type == 'div'
        assert vnode.props == {'id': 'test'}
        assert len(vnode.children) == 1
    
    def test_h_with_multiple_children(self):
        """Test element with multiple children"""
        vnode = h('div', None,
            h('span', None, 'Hello'),
            h('span', None, 'World')
        )
        assert len(vnode.children) == 2
    
    def test_h_with_key(self):
        """Test element with key"""
        vnode = h('div', {'key': 'test-key'}, 'Hello')
        assert vnode.key == 'test-key'
    
    def test_h_with_ref(self):
        """Test element with ref"""
        ref = {'current': None}
        vnode = h('div', {'ref': ref}, 'Hello')
        assert vnode.ref == ref
    
    def test_h_flatten_children(self):
        """Test children flattening"""
        vnode = h('div', None,
            [h('span', None, '1'), h('span', None, '2')],
            h('span', None, '3')
        )
        assert len(vnode.children) == 3
    
    def test_h_none_children(self):
        """Test that None children are filtered"""
        vnode = h('div', None, None, 'Hello', None)
        assert len(vnode.children) == 1


class TestCreateElement:
    """Tests for create_element function"""
    
    def test_create_element_alias(self):
        """Test that create_element is alias for h"""
        vnode1 = h('div', {'id': 'test'}, 'Hello')
        vnode2 = create_element('div', {'id': 'test'}, 'Hello')
        
        assert vnode1.type == vnode2.type
        assert vnode1.props == vnode2.props


class TestIsValidElement:
    """Tests for is_valid_element function"""
    
    def test_valid_element(self):
        """Test valid element check"""
        vnode = h('div', None, 'Hello')
        assert is_valid_element(vnode) is True
    
    def test_invalid_element(self):
        """Test invalid element check"""
        assert is_valid_element('div') is False
        assert is_valid_element(None) is False
        assert is_valid_element({}) is False


class TestCloneElement:
    """Tests for clone_element function"""
    
    def test_clone_element(self):
        """Test cloning element"""
        original = h('div', {'className': 'test'}, 'Hello')
        cloned = clone_element(original)
        
        assert original.type == cloned.type
        assert original is not cloned
    
    def test_clone_with_new_props(self):
        """Test cloning with new props"""
        original = h('div', {'className': 'test'}, 'Hello')
        cloned = clone_element(original, {'id': 'new-id'})
        
        assert cloned.props.get('id') == 'new-id'
        assert cloned.props.get('className') == 'test'


class TestComponent:
    """Tests for Component class"""
    
    def test_component_initialization(self):
        """Test component initialization"""
        class TestComponent(Component):
            def render(self):
                return h('div', None, 'Test')
        
        component = TestComponent({'name': 'test'})
        assert component.props == {'name': 'test'}
        assert component.state == {}
    
    def test_component_set_state(self):
        """Test set_state method"""
        class TestComponent(Component):
            def render(self):
                return h('div', None, 'Test')
        
        component = TestComponent({})
        component.state = {'count': 0}
        component.set_state({'count': 1})
        
        assert component.state['count'] == 1
    
    def test_component_functional_set_state(self):
        """Test functional set_state"""
        class TestComponent(Component):
            def render(self):
                return h('div', None, 'Test')
        
        component = TestComponent({})
        component.state = {'count': 0}
        component.set_state(lambda s: {'count': s['count'] + 1})
        
        assert component.state['count'] == 1
    
    def test_component_render(self):
        """Test component render method"""
        class TestComponent(Component):
            def render(self):
                return h('div', None, 'Test')
        
        component = TestComponent({})
        rendered = component.render()
        
        assert rendered.type == 'div'
        assert rendered.children[0] == 'Test'


class TestPureComponent:
    """Tests for PureComponent class"""
    
    def test_pure_component_should_update(self):
        """Test should_component_update"""
        class TestPure(PureComponent):
            def render(self):
                return h('div', None, 'Test')
        
        component = TestPure({'name': 'test'})
        
        # Same props - should not update
        assert component.should_component_update({'name': 'test'}, {}) is False
        
        # Different props - should update
        assert component.should_component_update({'name': 'other'}, {}) is True


class TestShallowEqual:
    """Tests for shallow_equal function"""
    
    def test_same_object(self):
        """Test same object comparison"""
        obj = {'a': 1}
        assert shallow_equal(obj, obj) is True
    
    def test_equal_objects(self):
        """Test equal objects comparison"""
        obj1 = {'a': 1, 'b': 2}
        obj2 = {'a': 1, 'b': 2}
        assert shallow_equal(obj1, obj2) is True
    
    def test_different_objects(self):
        """Test different objects comparison"""
        obj1 = {'a': 1}
        obj2 = {'a': 2}
        assert shallow_equal(obj1, obj2) is False
    
    def test_different_keys(self):
        """Test objects with different keys"""
        obj1 = {'a': 1}
        obj2 = {'b': 1}
        assert shallow_equal(obj1, obj2) is False


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
