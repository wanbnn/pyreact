"""
Tests for PyReact DOM Module
"""

import pytest
from pyreact.dom.dom_operations import (
    document,
    Element,
    TextNode,
    CommentNode,
    create_element,
    create_text_node,
    append_child,
    remove_child,
    set_attribute,
    remove_attribute,
)
from pyreact.dom.events import (
    SyntheticEvent,
    SyntheticMouseEvent,
    SyntheticKeyboardEvent,
    EVENT_TYPES,
    get_native_event_type,
)
from pyreact.dom.attributes import (
    is_custom_attribute,
    should_set_attribute,
    get_attribute_name,
    is_boolean_attribute,
    escape_html_value,
)


class TestDocument:
    """Tests for Document class"""
    
    def test_document_creation(self):
        """Test document creation"""
        assert document is not None
        assert document.body is not None
        assert document.head is not None
    
    def test_create_element(self):
        """Test create_element method"""
        elem = document.create_element('div')
        assert elem.tag_name == 'div'
    
    def test_create_text_node(self):
        """Test create_text_node method"""
        text = document.create_text_node('Hello')
        assert text.text_content == 'Hello'
    
    def test_get_element_by_id(self):
        """Test get_element_by_id method"""
        elem = document.create_element('div')
        elem.attributes['id'] = 'test-id'
        document.body.append_child(elem)
        
        found = document.get_element_by_id('test-id')
        assert found is not None


class TestElement:
    """Tests for Element class"""
    
    def test_element_creation(self):
        """Test element creation"""
        elem = Element('div')
        assert elem.tag_name == 'div'
    
    def test_append_child(self):
        """Test append_child method"""
        parent = Element('div')
        child = Element('span')
        
        parent.append_child(child)
        assert len(parent.child_nodes) == 1
        assert child.parent_node == parent
    
    def test_remove_child(self):
        """Test remove_child method"""
        parent = Element('div')
        child = Element('span')
        
        parent.append_child(child)
        parent.remove_child(child)
        
        assert len(parent.child_nodes) == 0
        assert child.parent_node is None
    
    def test_set_attribute(self):
        """Test setting attributes"""
        elem = Element('div')
        set_attribute(elem, 'id', 'test')
        
        assert elem.attributes['id'] == 'test'
    
    def test_remove_attribute(self):
        """Test removing attributes"""
        elem = Element('div')
        elem.attributes['id'] = 'test'
        remove_attribute(elem, 'id')
        
        assert 'id' not in elem.attributes
    
    def test_query_selector(self):
        """Test query_selector method"""
        parent = Element('div')
        child1 = Element('span')
        child1.attributes['id'] = 'child1'
        child2 = Element('span')
        child2.attributes['class'] = 'test-class'
        
        parent.append_child(child1)
        parent.append_child(child2)
        
        found = parent.query_selector('#child1')
        assert found == child1
        
        found = parent.query_selector('.test-class')
        assert found == child2


class TestTextNode:
    """Tests for TextNode class"""
    
    def test_text_node_creation(self):
        """Test text node creation"""
        text = TextNode('Hello World')
        assert text.text_content == 'Hello World'
        assert text.node_type == 'text'


class TestCommentNode:
    """Tests for CommentNode class"""
    
    def test_comment_node_creation(self):
        """Test comment node creation"""
        comment = CommentNode('This is a comment')
        assert comment.text_content == 'This is a comment'
        assert comment.node_type == 'comment'


class TestSyntheticEvent:
    """Tests for SyntheticEvent class"""
    
    def test_event_creation(self):
        """Test event creation"""
        event = SyntheticEvent({'type': 'click'})
        assert event.type == 'click'
    
    def test_stop_propagation(self):
        """Test stopPropagation method"""
        event = SyntheticEvent({})
        event.stop_propagation()
        assert event._propagation_stopped is True
    
    def test_prevent_default(self):
        """Test preventDefault method"""
        event = SyntheticEvent({})
        event.prevent_default()
        assert event._default_prevented is True
    
    def test_persist(self):
        """Test persist method"""
        event = SyntheticEvent({})
        event.persist()
        assert event._is_persisted is True


class TestSyntheticMouseEvent:
    """Tests for SyntheticMouseEvent class"""
    
    def test_mouse_event(self):
        """Test mouse event properties"""
        event = SyntheticMouseEvent({
            'type': 'click',
            'clientX': 100,
            'clientY': 200,
            'button': 0
        })
        
        assert event.client_x == 100
        assert event.client_y == 200
        assert event.button == 0


class TestSyntheticKeyboardEvent:
    """Tests for SyntheticKeyboardEvent class"""
    
    def test_keyboard_event(self):
        """Test keyboard event properties"""
        event = SyntheticKeyboardEvent({
            'type': 'keydown',
            'key': 'Enter',
            'code': 'Enter',
            'keyCode': 13
        })
        
        assert event.key == 'Enter'
        assert event.code == 'Enter'
        assert event.key_code == 13


class TestEventTypes:
    """Tests for EVENT_TYPES"""
    
    def test_event_types_exist(self):
        """Test that event types are defined"""
        assert 'onClick' in EVENT_TYPES
        assert 'onChange' in EVENT_TYPES
        assert 'onKeyDown' in EVENT_TYPES
    
    def test_get_native_event_type(self):
        """Test get_native_event_type function"""
        assert get_native_event_type('onClick') == 'click'
        assert get_native_event_type('onChange') == 'change'
        assert get_native_event_type('onKeyDown') == 'keydown'


class TestAttributes:
    """Tests for attribute utilities"""
    
    def test_is_custom_attribute(self):
        """Test is_custom_attribute function"""
        assert is_custom_attribute('data-test') is True
        assert is_custom_attribute('aria-label') is True
        assert is_custom_attribute('id') is False
    
    def test_should_set_attribute(self):
        """Test should_set_attribute function"""
        assert should_set_attribute('id', 'test') is True
        assert should_set_attribute('onClick', None) is False
        assert should_set_attribute('ref', None) is False
        assert should_set_attribute('key', None) is False
    
    def test_get_attribute_name(self):
        """Test get_attribute_name function"""
        assert get_attribute_name('className') == 'class'
        assert get_attribute_name('htmlFor') == 'for'
        assert get_attribute_name('id') == 'id'
    
    def test_is_boolean_attribute(self):
        """Test is_boolean_attribute function"""
        assert is_boolean_attribute('disabled') is True
        assert is_boolean_attribute('checked') is True
        assert is_boolean_attribute('id') is False
    
    def test_escape_html_value(self):
        """Test escape_html_value function"""
        assert escape_html_value('<script>') == '&lt;script&gt;'
        assert escape_html_value('a & b') == 'a &amp; b'
        assert escape_html_value('"test"') == '&quot;test&quot;'


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
