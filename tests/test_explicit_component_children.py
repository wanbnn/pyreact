from pyreact.core.element import clone_element, h
from pyreact.server import render_to_static_markup


def Echo(props):
    return h("span", None, *props.get("children", []))


def test_h_preserves_explicit_component_children_without_positional_children():
    node = h(Echo, {"children": "Continuar"})

    assert node.children == ["Continuar"]
    assert node.props["children"] == ["Continuar"]
    assert "Continuar" in render_to_static_markup(node)


def test_h_positional_children_override_explicit_children_prop():
    node = h(Echo, {"children": "antigo"}, "novo")

    assert node.children == ["novo"]
    assert node.props["children"] == ["novo"]
    assert "novo" in render_to_static_markup(node)
    assert "antigo" not in render_to_static_markup(node)


def test_h_explicit_component_children_are_normalized_like_positional_children():
    node = h(Echo, {"children": ["um", 2, None, False, ["tres"]]})

    assert node.children == ["um", "2", "tres"]
    assert node.props["children"] == ["um", "2", "tres"]


def test_clone_element_accepts_explicit_children_prop_override():
    original = h(Echo, None, "antigo")
    cloned = clone_element(original, {"children": "novo"})

    assert cloned.children == ["novo"]
    assert cloned.props["children"] == ["novo"]
    html = render_to_static_markup(cloned)
    assert "novo" in html
    assert "antigo" not in html


def test_clone_element_positional_children_still_take_precedence():
    original = h(Echo, None, "original")
    cloned = clone_element(original, {"children": "prop"}, "posicional")

    assert cloned.children == ["posicional"]
    assert cloned.props["children"] == ["posicional"]
