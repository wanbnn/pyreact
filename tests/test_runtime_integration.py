"""Integration coverage for rendering, hooks and testing utilities."""

from pyreact import h, use_state
from pyreact.testing import cleanup, fire_event, render


def test_function_component_rerenders_after_state_change():
    def Counter(props):
        count, set_count = use_state(0)
        return h(
            "button",
            {"role": "button", "onClick": lambda _: set_count(count + 1)},
            f"Count: {count}",
        )

    result = render(h(Counter, None))
    button = result.get_by_role("button")

    assert result.container.text_content == "Count: 0"
    fire_event(button, "click")
    assert result.container.text_content == "Count: 1"
    fire_event(result.get_by_role("button"), "click")
    assert result.container.text_content == "Count: 2"
    cleanup()


def test_rerender_replaces_text_without_duplicating_old_content():
    result = render(h("p", None, "before"))
    result.rerender(h("p", None, "after"))

    assert result.container.text_content == "after"
    cleanup()
