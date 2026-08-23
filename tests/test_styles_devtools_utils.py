import json

import pytest

from pyreact import h, render, styled
from pyreact.devtools.debugger import (
    Debugger, debug_component, get_component_tree, get_debugger,
)
from pyreact.devtools.profiler import (
    Profiler, get_profile_data, get_profiler, profile_component, start_profiling,
    stop_profiling,
)
from pyreact.dom.attributes import (
    escape_html_value, get_attribute_name, get_property_name, get_style_value,
    is_boolean_attribute, is_custom_attribute, is_property, render_attributes,
    should_set_attribute,
)
from pyreact.dom.dom_operations import (
    CommentNode, Element, append_child, create_element, create_text_node,
    dispatch_event, document, insert_before, remove_child, set_attribute,
    remove_attribute, set_style,
)
from pyreact.dom.events import (
    SyntheticAnimationEvent, SyntheticDragEvent, SyntheticEvent,
    SyntheticFocusEvent, SyntheticFormEvent, SyntheticKeyboardEvent,
    SyntheticMouseEvent, SyntheticTouchEvent, SyntheticTransitionEvent,
    create_synthetic_event, get_native_event_type,
)
from pyreact.styles.css_module import (
    CSSModuleManager, css_module, get_all_global_css, get_all_module_css,
    get_class_name, get_css_module_manager, load_css,
)
from pyreact.styles.styled import (
    StyleManager, create_global_style, css, get_all_styles, get_style_manager,
    get_style_registry, keyframes,
)
from pyreact.testing import cleanup
from pyreact.testing.fire_event import (
    FireEvent, blur, change, click, fire_event, focus, key_down, key_up,
    mouse_enter, mouse_leave, submit,
)
from pyreact.testing.screen import (
    Screen, find_by_role as global_find_by_role, find_by_test_id as global_find_by_test_id,
    find_by_text as global_find_by_text, get_by_role as global_get_by_role,
    get_by_test_id as global_get_by_test_id, get_by_text as global_get_by_text,
    query_by_role as global_query_by_role, query_by_test_id as global_query_by_test_id,
    query_by_text as global_query_by_text,
)
from pyreact.testing.test_renderer import act, render as render_component, render_to_json
from pyreact.utils.diff import (
    deep_compare, diff_objects, get_changed_props, merge_props, props_changed,
    shallow_compare,
)
from pyreact.utils.object_pool import (
    EventPool, ObjectPool, VNodePool, get_pool, register_pool,
)


def test_styled_css_keyframes_global_and_manager():
    Button = styled('button', 'color: red; &:hover { color: blue; }')
    host = document.create_element('div')
    render(h(Button, {'className': 'extra'}, 'Click'), host)
    class_name = host.first_child.attributes['class']
    assert 'extra' in class_name and 'pyreact-' in class_name
    assert ':hover' in get_all_styles()
    assert css('display: block;').startswith('pyreact-')
    assert keyframes('from { opacity: 0; } to { opacity: 1; }').startswith('pyreact-')
    Global = create_global_style('body { margin: 0; }')
    render(h(Global), document.create_element('div'))
    assert 'global' in get_style_registry()

    manager = StyleManager()
    manager.add_style('a', '.a{}')
    assert manager.get_css() == '.a{}'
    manager.inject(); manager.inject()
    manager.remove_style('a'); manager.clear()
    assert manager.get_css() == '' and get_style_manager() is not None


def test_css_modules_loading_cache_and_clear(tmp_path):
    path = tmp_path / 'Card.module.css'
    path.write_text('.card, .title { color: red; }\n.card:hover { color: blue; }', encoding='utf-8')
    module = css_module(str(path))
    assert set(module) == {'card', 'title'}
    assert get_class_name(module, 'card').endswith('__card')
    assert get_class_name(module, 'unknown') == 'unknown'
    assert '__card' in get_all_module_css()

    global_path = tmp_path / 'global.css'
    global_path.write_text('body { margin: 0; }', encoding='utf-8')
    assert load_css(str(global_path)).startswith('body')
    assert 'margin' in get_all_global_css()
    assert load_css(str(tmp_path / 'missing.css')) == ''

    manager = CSSModuleManager()
    first = manager.load_module(str(path))
    assert manager.load_module(str(path)) is first
    assert manager.get_module(str(path)) is first
    assert '__card' in manager.get_all_css()
    manager.clear()
    assert manager.get_module(str(path)) is None and get_css_module_manager() is not None


def test_debugger_complete_api(capsys):
    debugger = Debugger()
    component = type('Demo', (), {'props': {}, 'state': {}})()
    assert not debugger.is_enabled()
    debugger.register_component(component)
    debugger.enable()
    assert debugger.is_enabled()
    debugger.register_component(component)
    debugger.update_component_props(component, {'a': 1})
    debugger.update_component_state(component, {'count': 2})
    debugger.log_lifecycle_event(component, 'render', {'phase': 1})
    info = debugger.get_component_info(component)
    assert info['props'] == {'a': 1} and info['render_count'] == 1
    assert debugger.get_tree()['children'][0]['name'] == 'Demo'
    debugger.add_breakpoint('Demo', 'render')
    assert debugger.should_break('Demo', 'render')
    debugger.remove_breakpoint('Demo', 'render')
    debugger.watch('state.count'); debugger.watch('state.count'); debugger.unwatch('state.count')
    assert debugger.get_logs() and '[PyReact Debug]' in capsys.readouterr().out
    debugger.clear_logs(); debugger.unregister_component(component); debugger.disable(); debugger.clear_logs()
    assert not debugger.get_logs() and not debugger.is_enabled()
    assert get_debugger() is not None and isinstance(debug_component(component), dict)
    assert 'children' in get_component_tree()


def test_profiler_complete_api():
    profiler = Profiler()
    assert not profiler.is_enabled() and profiler.end_render('None') == 0
    assert profiler.end_commit() == 0
    profiler.start()
    profiler.begin_render('Fast'); duration = profiler.end_render('Fast')
    profiler.begin_commit(); commit = profiler.end_commit()
    profiler.log('custom', {'x': 1})
    report = profiler.get_report()
    assert duration >= 0 and commit >= 0 and report['render_count'] == 1
    assert profiler.get_slow_components(-1)[0]['name'] == 'Fast'
    assert json.loads(profiler.export())['commit_count'] == 1
    profiler.stop(); profiler.clear()

    global_profiler = get_profiler()
    start_profiling()
    global_profiler.begin_render('Demo'); global_profiler.end_render('Demo')
    component = type('Demo', (), {})()
    assert profile_component(component)['count'] >= 1
    assert get_profile_data()['render_count'] >= 1
    assert stop_profiling()['render_count'] >= 1


def test_diff_utilities_all_branches():
    added, removed, changed = diff_objects({'a': 1, 'b': 2}, {'a': 2, 'c': 3})
    assert added == {'a': 2, 'c': 3} and removed == {'b': 2} and set(changed) == {'a', 'c'}
    same = {'x': 1}
    assert shallow_compare(same, same)
    assert shallow_compare(1, 1) and not shallow_compare({}, [])
    assert not shallow_compare({'x': 1}, {'x': 1, 'y': 2})
    assert not shallow_compare({'x': 1}, {'x': 2})
    assert deep_compare(same, same) and not deep_compare([], ())
    assert deep_compare(1, 1) and not deep_compare(1, 2)
    assert deep_compare([1, {'x': 2}], [1, {'x': 2}])
    assert not deep_compare([1], [1, 2])
    assert not deep_compare({'x': 1}, {'x': 1, 'y': 2})
    assert not deep_compare({'x': 1}, {'y': 1})
    assert not deep_compare({'x': 1}, {'x': 2})
    assert props_changed({'a': 1}, {'a': 2})
    assert props_changed({'a': 1}, {'a': 2}, ['a'])
    assert not props_changed({'a': 1}, {'a': 1}, ['a'])
    assert set(get_changed_props({'a': 1}, {'b': 2})) == {'a', 'b'}
    assert merge_props({'a': 1}, {'a': 2}, {'b': 3}) == {'a': 2, 'b': 3}


def test_object_pools_all_paths():
    pool = ObjectPool(lambda: {'value': 0}, max_size=1,
                      reset=lambda item: item.update(value=0))
    first = pool.acquire(); first['value'] = 2
    assert pool.in_use_count() == 1 and pool.total_count() == 1
    pool.release(first); pool.release(first)
    assert pool.size() == 1
    assert pool.acquire() is first and first['value'] == 0
    second = pool.acquire()
    pool.release(first); pool.release(second)
    assert pool.size() == 1
    pool.clear(); assert pool.total_count() == 0

    vnode_pool = VNodePool(1); vnode = vnode_pool.acquire(); vnode['type'] = 'div'
    vnode_pool.release(vnode); assert vnode_pool.acquire()['type'] is None
    event_pool = EventPool(1); event = event_pool.acquire(); event['type'] = 'click'
    event_pool.release(event); assert event_pool.acquire()['type'] == ''
    register_pool('custom', pool)
    assert get_pool('custom') is pool and get_pool('missing') is None
    assert get_pool('vnode') is not None and get_pool('event') is not None


def test_dom_operations_attributes_events_and_queries():
    parent, a, b = create_element('div'), create_element('button'), create_element('span')
    append_child(parent, a); insert_before(parent, b, a)
    assert parent.first_child is b
    remove_child(parent, b); insert_before(parent, b, None)
    parent.move_child(1, 0); parent.replace_child_at(create_element('i'), 0)
    parent.remove_child_at(0); parent.remove_child_at(99)
    set_attribute(a, 'id', 'action'); set_style(a, {'color': 'red'})
    assert a.get_attribute('id') == 'action' and a.style['color'] == 'red'
    remove_attribute(a, 'id'); remove_attribute(a, 'missing')
    a.set_attribute('class', 'one two'); parent.append_child(a)
    assert parent.query_selector('.one') is a and parent.query_selector('button') is a
    assert parent.query_selector('#missing') is None
    assert a in parent.query_selector_all('.two')
    assert parent.get_element_by_id('none') is None
    assert a.get_bounding_client_rect()['width'] == 0
    a.scroll_into_view()

    calls = []
    a.add_event_listener('click', lambda event: calls.append(event.type))
    a.click(); a.focus(); a.blur()
    assert calls == ['click']
    a.remove_event_listener('click', a._event_listeners['click'][0])
    a.add_event_listener('click', lambda event: None); a.remove_event_listener('click')
    dispatch_event(a, 'missing')

    text = create_text_node('hello')
    assert 'hello' in repr(text) and repr(a) == '<button>'
    comment = document.create_comment('note'); assert isinstance(comment, CommentNode)
    assert document.create_element('DIV').tag_name == 'div'

    assert is_custom_attribute('data-x') and is_custom_attribute('aria-label')
    assert not should_set_attribute('onClick', lambda: None)
    assert not should_set_attribute('style', {}) and not should_set_attribute('ref', None)
    assert should_set_attribute('id', 'x')
    assert get_attribute_name('htmlFor') == 'for' and get_property_name('for') == 'htmlFor'
    assert is_boolean_attribute('disabled') and is_property('value')
    assert get_style_value('width', 2) == '2px' and get_style_value('opacity', 1) == '1'
    assert get_style_value('width', None) == '' and get_style_value('color', 'red') == 'red'
    assert escape_html_value('<&>') == '&lt;&amp;&gt;'
    attrs = render_attributes({'disabled': True, 'hidden': False, 'className': 'x'})
    assert 'disabled' in attrs and 'hidden' not in attrs and 'class="x"' in attrs


def test_synthetic_event_families_and_native_bridge():
    base = SyntheticEvent({'type': 'custom', 'target': 'x', 'currentTarget': 'y'})
    base.stop_propagation(); base.prevent_default(); base.persist()
    assert base.is_propagation_stopped() and base.is_default_prevented()
    assert 'custom' in repr(base)
    mouse = SyntheticMouseEvent({'clientX': 1, 'shiftKey': True})
    assert mouse.client_x == 1 and mouse.get_modifier_state('Shift')
    assert not mouse.get_modifier_state('Unknown')
    key = SyntheticKeyboardEvent({'key': 'Enter', 'ctrlKey': True})
    assert key.key == 'Enter' and key.get_modifier_state('Control')
    assert isinstance(SyntheticFocusEvent({}), SyntheticEvent)
    form = SyntheticFormEvent({'target': {'value': 'x', 'checked': True}})
    assert form.value == 'x' and form.checked
    assert SyntheticTouchEvent({'touches': [1]}).touches == [1]
    assert SyntheticDragEvent({'dataTransfer': 'd'}).data_transfer == 'd'
    assert SyntheticAnimationEvent({'animationName': 'fade'}).animation_name == 'fade'
    assert SyntheticTransitionEvent({'propertyName': 'color'}).property_name == 'color'
    for event_type in ('click', 'keydown', 'focus', 'change', 'touchstart', 'drag',
                       'animationend', 'transitionend', 'unknown'):
        assert isinstance(create_synthetic_event(event_type, {'type': event_type}), SyntheticEvent)
    assert get_native_event_type('onClick') == 'click' and get_native_event_type('change') == 'change'


def test_testing_screen_renderer_and_fire_event_helpers():
    changed = []
    vnode = h('form', {'role': 'form', 'onSubmit': lambda event: changed.append('submit')},
              h('label', {'htmlFor': 'name'}, 'Name'),
              h('input', {'id': 'name', 'placeholder': 'Your name', 'value': 'Ada',
                          'data-testid': 'name', 'onChange': lambda event: changed.append(event.value)}),
              h('button', {'role': 'button', 'onClick': lambda event: changed.append('click')}, 'Save'))
    result = render_component(vnode)
    assert result.get_by_text('Save') and result.get_by_test_id('name')
    assert result.get_by_role('button') and result.query_by_text('missing') is None
    assert result.query_all_by_text('Save') and result.get_all_by_text('Save')
    with pytest.raises(ValueError): result.get_by_text('missing')
    with pytest.raises(ValueError): result.get_by_test_id('missing')
    with pytest.raises(ValueError): result.get_by_role('missing')
    with pytest.raises(ValueError): result.get_all_by_text('missing')

    screen = Screen(); screen.set_container(result.container)
    input_node = result.get_by_test_id('name')
    button = result.get_by_role('button')
    assert screen.get_by_text('Save') and screen.find_by_text('Save')
    assert screen.get_by_role('button') and screen.find_by_role('button')
    assert screen.get_by_test_id('name') and screen.find_by_test_id('name')
    assert screen.get_by_placeholder_text('Your name')
    assert screen.query_by_placeholder_text('Your name')
    assert screen.get_by_label_text('Name') is input_node
    assert screen.query_by_label_text('missing') is None
    assert screen.get_by_display_value('Ada')
    assert screen.query_by_display_value('missing') is None
    assert screen.query_by_text('missing') is None
    assert screen.query_by_role('missing') is None and screen.query_by_test_id('missing') is None
    assert screen.get_all_by_text('Save') and screen.get_all_by_role('button')
    assert screen.query_all_by_text('Save') and screen.query_all_by_role('button')
    empty = Screen()
    assert empty.query_by_text('x') is None and empty.query_all_by_text('x') == []
    with pytest.raises(ValueError): empty.get_by_text('x')

    fire_event(button, 'click')
    fire_event(input_node, 'change', {'target': {'value': 'Grace'}})
    for event_name in ('input', 'focus', 'blur', 'keydown', 'keyup', 'mouseenter',
                       'mouseleave', 'mousedown', 'mouseup', 'custom'):
        fire_event(input_node, event_name, {'key': 'A'})
    assert 'click' in changed and 'Grace' in changed
    click(button); change(input_node, {'target': {'value': 'Katherine'}})
    submit(result.container.first_child); focus(input_node); blur(input_node)
    key_down(input_node, 'A'); key_up(input_node, 'A')
    mouse_enter(input_node); mouse_leave(input_node)
    assert 'submit' in changed

    assert global_get_by_text('Save') and global_get_by_role('button')
    assert global_get_by_test_id('name') and global_query_by_text('missing') is None
    assert global_query_by_role('missing') is None and global_query_by_test_id('missing') is None
    assert global_find_by_text('Save') and global_find_by_role('button')
    assert global_find_by_test_id('name')

    string_screen = Screen(); string_screen.set_container('hello')
    assert string_screen.get_by_text('hell') == 'hello'
    assert string_screen.get_all_by_text('hell') == ['hello']
    act(lambda: None)
    assert render_to_json(h('p', {'id': 'x'}, 'text'))['children'] == ['text']
    assert render_to_json('text') == 'text'
    with pytest.raises(ValueError): render_component(object())
    result.unmount(); cleanup()
