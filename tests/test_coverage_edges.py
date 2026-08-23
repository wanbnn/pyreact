import asyncio
from types import SimpleNamespace

import pytest

from pyreact import Component, ErrorBoundary, create_context, create_ref, h, hydrate, render, use_state
from pyreact.core.element import VNode, clone_element
from pyreact.core.hooks import (
    _get_current_component, _set_current_component, use_debug_value,
    use_imperative_handle,
)
from pyreact.core.refs import Ref, attach_ref
from pyreact.dom.dom_operations import CommentNode, Element, TextNode, document
from pyreact.server.hydration import (
    HydrationContext, HydrationManager, HydrationMismatchError,
    check_hydration_mismatch, get_hydration_manager, hydrate_root,
    suppress_hydration_warning, use_hydration,
)
from pyreact.server.ssr import (
    SSRContext, _render_attrs, _render_node, _render_style, _stream_node,
    render_to_async_stream, render_to_static_markup, render_to_string,
    render_to_string_with_context,
)


def host():
    return document.create_element('div')


def test_component_base_state_callbacks_force_and_lifecycle_defaults():
    class Demo(Component):
        def render(self): return h('p', None, self.state.get('value', 0))

    component = Demo()
    assert Component.render(component) is None
    called = []
    component._is_rendering = True
    component.set_state(lambda state: {'value': 1}, lambda: called.append('queued'))
    assert component._pending_state == {'value': 1}
    component._is_rendering = False
    component.set_state({'other': 2}, lambda: called.append('applied'))
    assert component.state == {'value': 1, 'other': 2}
    assert called == ['queued', 'applied']
    assert not component._apply_state()
    component.force_update(lambda: called.append('forced'))
    assert component._force_update and called[-1] == 'forced'
    assert component.get_derived_state_from_props({}, {}) is None
    assert component.get_derived_state_from_error(ValueError()) is None
    assert component.should_component_update({}, {})
    component.component_will_mount(); component.component_did_mount()
    component.component_will_receive_props({}); component.component_will_update({}, {})
    component.component_did_update({}, {}); component.component_will_unmount()
    component.component_did_catch(ValueError(), {})
    assert repr(component) == '<Demo>'
    with pytest.raises(TypeError): Component()


def test_class_lifecycle_derived_state_and_force_update():
    events = []

    class Lifecycle(Component):
        def __init__(self, props=None):
            super().__init__(props); self.state = {'derived': 0}
        @staticmethod
        def get_derived_state_from_props(props, state):
            return {'derived': props.get('value', 0)}
        def component_will_mount(self): events.append('will-mount')
        def component_did_mount(self): events.append('did-mount')
        def component_will_receive_props(self, props): events.append('receive')
        def component_will_update(self, props, state): events.append('will-update')
        def component_did_update(self, props, state): events.append('did-update')
        def component_will_unmount(self): events.append('unmount')
        def render(self): return h('p', None, self.state['derived'])

    root = render(h(Lifecycle, {'value': 1}), host())
    instance = root._current_vnode._component_instance
    assert root.container.text_content == '1'
    root.render(h(Lifecycle, {'value': 2}))
    instance.force_update()
    root.unmount()
    assert {'will-mount', 'did-mount', 'receive', 'will-update', 'did-update', 'unmount'} <= set(events)


def test_element_edge_cases_and_clone_metadata():
    def Child(props): return h('span')
    vnode = h(Child, {'key': 'old'}, (h('i'), [1, False, None, 'x']))
    assert vnode.props['children'][1:] == ['1', 'x']
    cloned = clone_element(vnode, {'key': 'new', 'ref': 'ref'}, h('b'), 2)
    assert cloned.key == 'new' and cloned.ref == 'ref' and cloned.children[1] == '2'
    with pytest.raises(ValueError): clone_element('bad')
    with pytest.raises(TypeError, match='Unsupported child'):
        h('div', None, object())
    assert VNode(lambda: None).__repr__().startswith('VNode')
    assert VNode('a') != 'a'


def test_hook_context_errors_debug_and_imperative_none():
    _set_current_component(None)
    with pytest.raises(RuntimeError): _get_current_component()
    use_debug_value('value', str)

    captured = {}
    def App(props):
        use_imperative_handle(None, lambda: captured, [])
        return h('div')
    render(h(App), host())


def test_component_none_transitions_and_child_reconciliation_edges():
    def Maybe(props):
        return h('span', None, 'shown') if props['show'] else None
    container = host()
    root = render(h(Maybe, {'show': False}), container)
    assert isinstance(container.first_child, CommentNode)
    root.render(h(Maybe, {'show': True})); assert container.text_content == 'shown'
    root.render(h(Maybe, {'show': False})); assert isinstance(container.first_child, CommentNode)

    root = render(h('div', None, 'text', h('b', None, 'bold')), container)
    root.render(h('div', None, h('i', None, 'italic'), 'plain'))
    assert container.text_content == 'italicplain'
    root.render(h('div', None, 'only'))
    assert container.text_content == 'only'
    root.render(h('div', None, 'only', h('u', None, 'new')))
    assert container.text_content == 'onlynew'


def test_hydration_components_text_raw_and_all_mismatches():
    def Counter(props):
        value, _ = use_state(1)
        return h('button', None, value)
    container = host(); existing = Element('button'); existing.append_child(TextNode('1')); container.append_child(existing)
    root = hydrate_root(container, h(Counter))
    assert root.container.first_child is existing

    text = TextNode('x')
    from pyreact.core.reconciler import Reconciler
    reconciler = Reconciler()
    assert reconciler.hydrate_dom(VNode('#text', None, ['x']), text) is text
    with pytest.raises(HydrationMismatchError, match='Text mismatch'):
        reconciler.hydrate_dom(VNode('#text', None, ['y']), text)
    with pytest.raises(HydrationMismatchError, match='Expected element'):
        reconciler.hydrate_dom(h('div'), TextNode('x'))

    div = Element('div'); div.append_child(TextNode('server'))
    with pytest.raises(HydrationMismatchError, match='Text mismatch'):
        reconciler.hydrate_dom(h('div', None, 'client'), div)
    with pytest.raises(HydrationMismatchError, match='Child count'):
        reconciler.hydrate_dom(h('div'), div)
    raw = Element('div'); raw.set_inner_html('<b>x</b>')
    assert reconciler.hydrate_dom(h('div', {'dangerouslySetInnerHTML': {'__html': '<b>x</b>'}}), raw)


def test_hydration_context_manager_helpers_and_comparisons():
    context = HydrationContext(); error = ValueError('x')
    context.start_hydration(); context.add_error(error); context.add_warning('warning')
    assert context.is_hydrating and context.errors == [error] and context.warnings == ['warning']
    context.end_hydration(); assert not context.is_hydrating
    assert check_hydration_mismatch(Element('span'), h('div'), 'root')
    assert check_hydration_mismatch('server', 'client', 'root')
    assert check_hydration_mismatch('same', 'same') is None
    suppress_hydration_warning()
    assert use_hydration() == {'is_hydrating': False, 'is_hydrated': True}

    manager = HydrationManager()
    container = host(); container.append_child(Element('div'))
    manager.hydrate_root(container, h('div'))
    manager._context.add_error(error); manager._context.add_warning('w')
    assert manager.has_errors() and manager.get_errors() == [error]
    assert manager.get_warnings() == ['w'] and get_hydration_manager() is not None
    mismatch = HydrationMismatchError('bad', 's', 'c')
    assert mismatch.server_html == 's' and str(mismatch) == 'bad'


def test_ssr_all_component_result_error_context_and_attr_edges(capsys):
    assert render_to_static_markup(None) == ''
    assert render_to_static_markup('<x>') == '&lt;x&gt;'
    assert _render_node(None) == ''
    assert _render_style(123) == ''
    assert _render_attrs({}, False) == ''
    attrs = _render_attrs({'ref': 1, 'key': 2, 'children': [], 'htmlFor': 'x',
                           'dangerouslySetInnerHTML': {'__html': 'x'}, 'title': None}, False)
    assert attrs == ' for="x"'

    def Empty(props): return None
    def EmptyList(props): return []
    def OneList(props): return [h('i', None, 'one')]
    def Many(props): return [h('i'), h('b')]
    assert render_to_string(h(Empty)) == '' and render_to_string(h(EmptyList)) == ''
    assert 'one' in render_to_string(h(OneList))
    with pytest.raises(TypeError, match='one VNode'):
        render_to_string(h(Many))

    def Broken(props): raise RuntimeError('ssr')
    html = render_to_string(h(ErrorBoundary, {'fallback': h('p', None, 'fallback')}, h(Broken)))
    assert 'fallback' in html and 'caught an error' in capsys.readouterr().out

    context = create_context('light')
    def Themed(props):
        from pyreact import use_context
        return h('span', None, use_context(context))
    assert 'dark' in render_to_string(h(context.Provider, {'value': 'dark'}, h(Themed)))

    with pytest.raises(ValueError): _render_node(h('div', {'dangerouslySetInnerHTML': 'bad'}))
    assert list(_stream_node(None)) == []
    with pytest.raises(ValueError):
        list(_stream_node(h('div', {'dangerouslySetInnerHTML': 'bad'})))

    async def static_stream():
        return ''.join([part async for part in render_to_async_stream(h('p', None, 'x'), static=True)])
    assert 'data-reactroot' not in asyncio.run(static_stream())


def test_ssr_context_stack_and_render_wrapper():
    context = create_context('default')
    provider = SimpleNamespace(context=context, value='provided')
    ssr_context = SSRContext()
    assert ssr_context.pop_provider() is None
    ssr_context.push_provider(provider)
    assert ssr_context.get_context_value(context) == 'provided'
    assert ssr_context.pop_provider() is provider
    assert ssr_context.get_context_value(context) == 'default'
    assert 'ok' in render_to_string_with_context(h('p', None, 'ok'), ssr_context)

