import asyncio
from types import SimpleNamespace

import pytest

from pyreact import (
    Component, ErrorBoundary, PureComponent, create_context, create_portal,
    create_ref, forward_ref, h, hydrate, lazy, memo, render, use_context,
    use_deferred_value, use_effect, use_id, use_imperative_handle,
    use_layout_effect, use_reducer, use_ref, use_state, use_transition,
)
from pyreact.core.error_boundary import ErrorInfo, capture_error, with_error_boundary
from pyreact.core.memo import Suspense, are_props_shallow_equal, shallow_compare
from pyreact.core.portal import (
    PortalManager, get_portal_manager, is_portal, render_portal, unmount_portal,
)
from pyreact.core.refs import (
    CallbackRef, attach_ref, create_callback_ref, detach_ref, is_ref,
    use_imperative_handle as legacy_use_imperative_handle,
)
from pyreact.core.reconciler import Reconciler
from pyreact.core.renderer import find_dom_node, unmount_component_at_node
from pyreact.core.scheduler import (
    Priority, Scheduler, Task, UpdateScheduler, batch_updates, get_scheduler,
    get_timeout_for_priority, get_update_scheduler, schedule_callback,
)
from pyreact.dom.dom_operations import document
from pyreact.server.hydration import HydrationMismatchError


def container():
    return document.create_element('div')


def test_children_context_forward_ref_and_imperative_handle():
    theme = create_context('light')
    seen = []

    @forward_ref
    def Field(props, ref):
        use_imperative_handle(ref, lambda: {'focus': 'ok'}, [])
        return h('span', {'ref': use_ref()}, use_context(theme), props['children'])

    ref = create_ref()
    root_node = container()
    render(h(theme.Provider, {'value': 'dark'}, h(Field, {'ref': ref}, '!')), root_node)
    assert root_node.text_content == 'dark!'
    assert ref.current == {'focus': 'ok'}

    callback = create_callback_ref(seen.append)
    assert isinstance(callback, CallbackRef) and is_ref(callback) and is_ref(ref)
    attach_ref(callback, 'node')
    detach_ref(callback)
    assert seen == ['node', None]
    attach_ref(None, 'ignored')
    direct = []
    attach_ref(direct.append, 'callback')
    assert direct == ['callback']

    legacy_ref = create_ref()
    def Legacy(props):
        legacy_use_imperative_handle(legacy_ref, lambda: 'legacy', [])
        return h('i')
    render(h(Legacy), container())
    assert legacy_ref.current == 'legacy'


def test_context_consumer_manager_and_invalid_multiple_roots():
    context = create_context('base')
    assert context._get_value() == 'base'
    context._push_provider(1, 'one')
    assert context._get_value() == 'one'
    context._pop_provider(1)
    assert context._get_value() == 'base'

    from pyreact.core.context import ContextManager, get_context_manager
    manager = ContextManager()
    manager.register(context)
    assert manager.get_context(context._id) is context
    manager.unregister(context)
    assert manager.get_context(context._id) is None
    assert get_context_manager() is not None

    with pytest.raises(TypeError):
        render(h(context.Provider, None, h('i'), h('b')), container())

    output = container()
    render(h(context.Consumer, None, lambda value: h('b', None, value)), output)
    assert output.text_content == 'base'


def test_effect_order_cleanup_and_hook_count_validation():
    calls = []

    def App(props):
        def layout():
            calls.append('layout')
            return lambda: calls.append('unlayout')
        def effect():
            calls.append('effect')
            return lambda: calls.append('uneffect')
        use_layout_effect(layout, [])
        use_effect(effect, [])
        return h('div', None, 'ok')

    host = container()
    root = render(h(App), host)
    assert calls == ['layout', 'effect']
    root.unmount()
    assert calls == ['layout', 'effect', 'unlayout', 'uneffect']

    def Conditional(props):
        use_state(0)
        if props['extra']:
            use_ref(None)
        return h('p')

    host = container()
    root = render(h(Conditional, {'extra': True}), host)
    with pytest.raises(RuntimeError, match='Hook count'):
        root.render(h(Conditional, {'extra': False}))


def test_reducer_transition_deferred_and_stable_ids():
    captured = {}

    def App(props):
        state, dispatch = use_reducer(lambda value, amount: value + amount, 1)
        start, pending = use_transition()
        captured.update(dispatch=dispatch, start=start, pending=pending)
        return h('output', {'id': use_id()}, use_deferred_value(state))

    host = container()
    root = render(h(App), host)
    element = host.first_child
    first_id = element.attributes['id']
    captured['dispatch'](2)
    assert host.text_content == '3' and host.first_child.attributes['id'] == first_id
    captured['start'](lambda: captured['dispatch'](1))
    assert host.text_content == '4'


def test_error_boundaries_and_helpers(capsys):
    def Broken(props):
        raise RuntimeError('failure')

    host = container()
    render(h(ErrorBoundary, {'fallback': h('p', None, 'recovered')}, h(Broken)), host)
    assert host.text_content == 'recovered'
    assert 'caught an error' in capsys.readouterr().out
    assert ErrorInfo('A > B').to_dict()['componentStack'] == 'A > B'
    assert capture_error(ValueError('x'))['errorInfo']['componentStack'] == ''

    wrapped = with_error_boundary(Broken, h('span', None, 'wrapped'))
    host = container()
    render(h(wrapped), host)
    assert host.text_content == 'wrapped'


def test_memo_pure_component_lazy_and_suspense():
    renders = []

    @memo
    def Label(props):
        renders.append(props['value'])
        return h('span', None, props['value'])

    host = container()
    root = render(h(Label, {'value': 'a'}), host)
    root.render(h(Label, {'value': 'a'}))
    root.render(h(Label, {'value': 'b'}))
    assert renders == ['a', 'b']
    assert are_props_shallow_equal({'a': 1}, {'a': 1})
    assert shallow_compare({'a': 1}, {'a': 1}, {'x': 1}, {'x': 1})
    assert not shallow_compare({'a': 1}, {'a': 2})

    Loaded = lazy(lambda: SimpleNamespace(default=lambda props: h('strong', None, 'ready')))
    host = container()
    render(h(Loaded), host)
    assert host.text_content == 'ready'

    assert Suspense({'fallback': h('i', None, 'wait')}).render().children == ['wait']
    child = h('b', None, 'done')
    assert Suspense({'children': child}).render() is child


def test_portal_lifecycle_and_manager():
    target = container()
    portal = create_portal(h('aside', None, 'modal'), target)
    assert is_portal(portal) and 'Portal' in repr(portal)
    host = container()
    root = render(h('main', None, portal), host)
    assert target.text_content == 'modal'
    root.unmount()
    assert not target.child_nodes

    manager = PortalManager()
    identifier = manager.register(portal)
    assert manager.get_portal(identifier) is portal
    manager.unregister(portal)
    assert manager.get_portal(identifier) is None
    manager.register(portal)
    manager.unmount_all()
    assert get_portal_manager() is not None

    target.append_child(document.create_element('old'))
    list_portal = create_portal([h('i', None, 'one'), 'ignored', h('b', None, 'two')], target)
    render_portal(list_portal, Reconciler())
    assert target.text_content == 'onetwo' and len(list_portal._dom_nodes) == 2
    unmount_portal(list_portal)
    assert not target.child_nodes


def test_keyed_reconciliation_props_and_renderer_helpers():
    first_a, first_b = create_ref(), create_ref()
    host = container()
    root = render(h('ul', {'style': {'color': 'red', 'margin': '1px'}},
                    h('li', {'key': 'a', 'ref': first_a}, 'A'),
                    h('li', {'key': 'b', 'ref': first_b}, 'B')), host)
    old_a, old_b = first_a.current, first_b.current
    second_a, second_b = create_ref(), create_ref()
    root.render(h('ul', {'style': {'color': 'blue'}, 'hidden': False},
                  h('li', {'key': 'b', 'ref': second_b}, 'B'),
                  h('li', {'key': 'a', 'ref': second_a}, 'A'),
                  h('li', {'key': 'c'}, 'C')))
    assert second_a.current is old_a and second_b.current is old_b
    assert host.text_content == 'BAC' and host.first_child.style == {'color': 'blue'}
    root.render(h('section', None, 'replacement'))
    assert host.first_child.tag_name == 'section'
    root.render(None)
    assert host.first_child is None
    assert unmount_component_at_node(host)


def test_hydration_success_mismatches_and_events():
    calls = []
    host = container()
    existing = document.create_element('button')
    existing.append_child(document.create_text_node('Go'))
    host.append_child(existing)
    hydrate(h('button', {'onClick': lambda event: calls.append(event.type)}, 'Go'), host)
    assert host.first_child is existing
    existing.click()
    assert calls == ['click']

    wrong = container()
    wrong.append_child(document.create_element('span'))
    with pytest.raises(HydrationMismatchError, match='Tag mismatch'):
        hydrate(h('div'), wrong)

    multiple = container()
    multiple.append_child(document.create_element('i'))
    multiple.append_child(document.create_element('b'))
    with pytest.raises(HydrationMismatchError, match='exactly one'):
        hydrate(h('div'), multiple)


def test_scheduler_priorities_cancellation_batching_and_globals():
    assert get_timeout_for_priority(Priority.IMMEDIATE) == 0
    assert get_timeout_for_priority(Priority.IDLE) == float('inf')
    called = []
    scheduler = Scheduler()
    task = scheduler.schedule_callback(lambda: called.append('now'), Priority.IMMEDIATE)
    assert task.completed and called == ['now'] and scheduler.is_empty()
    assert scheduler.get_first_task() is None and scheduler.get_pending_count() == 0
    assert not scheduler.cancel_task(task)
    assert Task(lambda: None, Priority.NORMAL, 0) < Task(lambda: None, Priority.LOW, 0)

    class State:
        def __init__(self): self.applied = 0
        def _apply_state(self): self.applied += 1
        def render(self): self.applied += 1
    state = State()
    updates = UpdateScheduler()
    updates.batch_updates(lambda: updates.schedule_update(state))
    assert state.applied == 2
    updates.defer_update(state)
    updates.immediate_update(state)
    assert get_scheduler() and get_update_scheduler()
    assert schedule_callback(lambda: called.append('global')).completed
    batch_updates(lambda: None)
