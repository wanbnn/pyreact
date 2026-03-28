"""
Tests for PyReact Server-Side Rendering Module
"""

import pytest
from pyreact.core.element import h, VNode
from pyreact.server.ssr import (
    render_to_string,
    render_to_static_markup,
    escape_html,
    _render_attrs,
    _render_style,
    _camel_to_kebab,
)
from pyreact.core.component import Component


class TestRenderToString:
    """Tests for render_to_string function"""
    
    def test_simple_element(self):
        """Test rendering simple element"""
        vnode = h('div', {'id': 'test'}, 'Hello World')
        html = render_to_string(vnode)
        
        assert '<div' in html
        assert 'id="test"' in html
        assert 'Hello World' in html
        assert '</div>' in html
    
    def test_nested_elements(self):
        """Test rendering nested elements"""
        vnode = h('div', {'className': 'container'},
            h('h1', None, 'Title'),
            h('p', None, 'Paragraph')
        )
        html = render_to_string(vnode)
        
        assert '<div' in html
        assert '<h1>' in html
        assert 'Title' in html
        assert '<p>' in html
        assert 'Paragraph' in html
    
    def test_void_elements(self):
        """Test rendering void elements"""
        vnode = h('input', {'type': 'text', 'value': 'test'})
        html = render_to_string(vnode)
        
        assert '<input' in html
        assert 'type="text"' in html
        # Void elements should be self-closing
        assert '/>' in html or '>' in html
    
    def test_with_data_attrs(self):
        """Test that data attributes are included"""
        vnode = h('div', None, 'Test')
        html = render_to_string(vnode)
        
        assert 'data-reactroot' in html
    
    def test_string_child(self):
        """Test rendering string child"""
        html = render_to_string('Hello World')
        assert html == 'Hello World'
    
    def test_none_element(self):
        """Test rendering None"""
        html = render_to_string(None)
        assert html == ''


class TestRenderToStaticMarkup:
    """Tests for render_to_static_markup function"""
    
    def test_without_data_attrs(self):
        """Test that data attributes are not included"""
        vnode = h('div', None, 'Test')
        html = render_to_static_markup(vnode)
        
        assert 'data-reactroot' not in html
        assert 'Test' in html


class TestEscapeHtml:
    """Tests for escape_html function"""
    
    def test_escape_special_chars(self):
        """Test escaping special characters"""
        assert escape_html('<') == '&lt;'
        assert escape_html('>') == '&gt;'
        assert escape_html('&') == '&amp;'
        assert escape_html('"') == '&quot;'
        assert escape_html("'") == '&#x27;'
    
    def test_escape_full_string(self):
        """Test escaping full string"""
        result = escape_html('<script>alert("XSS")</script>')
        assert '<script>' not in result
        assert '&lt;script&gt;' in result


class TestRenderAttrs:
    """Tests for _render_attrs function"""
    
    def test_basic_attrs(self):
        """Test rendering basic attributes"""
        attrs = _render_attrs({'id': 'test', 'className': 'container'}, True)
        
        assert 'id="test"' in attrs
        assert 'class="container"' in attrs
    
    def test_boolean_attrs(self):
        """Test rendering boolean attributes"""
        attrs = _render_attrs({'disabled': True}, True)
        assert 'disabled' in attrs
    
    def test_false_boolean_attrs(self):
        """Test that false boolean attrs are not rendered"""
        attrs = _render_attrs({'disabled': False}, True)
        assert 'disabled' not in attrs
    
    def test_event_handlers_skipped(self):
        """Test that event handlers are skipped"""
        attrs = _render_attrs({'onClick': lambda e: None}, True)
        assert 'onClick' not in attrs
    
    def test_style_attr(self):
        """Test style attribute rendering"""
        attrs = _render_attrs({'style': {'color': 'red', 'fontSize': '16px'}}, True)
        assert 'style=' in attrs
        assert 'color:red' in attrs
        assert 'font-size:16px' in attrs


class TestRenderStyle:
    """Tests for _render_style function"""
    
    def test_string_style(self):
        """Test string style"""
        result = _render_style('color: red;')
        assert result == 'color: red;'
    
    def test_dict_style(self):
        """Test dict style"""
        result = _render_style({'color': 'red', 'fontSize': '16px'})
        assert 'color:red' in result
        assert 'font-size:16px' in result
    
    def test_empty_style(self):
        """Test empty style"""
        result = _render_style({})
        assert result == ''


class TestCamelToKebab:
    """Tests for _camel_to_kebab function"""
    
    def test_simple_conversion(self):
        """Test simple conversion"""
        assert _camel_to_kebab('backgroundColor') == 'background-color'
        assert _camel_to_kebab('fontSize') == 'font-size'
        assert _camel_to_kebab('marginTop') == 'margin-top'
    
    def test_single_word(self):
        """Test single word"""
        assert _camel_to_kebab('color') == 'color'
        assert _camel_to_kebab('margin') == 'margin'


class TestComponentRendering:
    """Tests for component rendering"""
    
    def test_function_component(self):
        """Test rendering function component"""
        def MyComponent(props):
            return h('div', None, f"Hello, {props['name']}!")
        
        vnode = h(MyComponent, {'name': 'World'})
        html = render_to_string(vnode)
        
        assert 'Hello, World!' in html
    
    def test_class_component(self):
        """Test rendering class component"""
        class MyComponent(Component):
            def render(self):
                return h('div', None, f"Hello, {self.props['name']}!")
        
        vnode = h(MyComponent, {'name': 'World'})
        html = render_to_string(vnode)
        
        assert 'Hello, World!' in html


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
