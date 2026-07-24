"""Integration tests for the Orbit application running on PyReact's Python DOM."""

from pyreact import h, render_to_static_markup
from pyreact.testing import cleanup, fire_event, render

from src.components import StatCard
from src.index import App


def test_dashboard_renders_seed_data_and_metrics():
    result = render(h(App, {"title": "Orbit Board"}))

    assert "Orbit Board" in result.container.text_content
    assert "Revisar página inicial" in result.container.text_content
    assert result.get_by_test_id("stat-total").text_content == "Total3"
    assert result.get_by_test_id("stat-concluídas").text_content == "Concluídas1"
    cleanup()


def test_adding_and_completing_a_task_updates_derived_metrics():
    result = render(h(App, {"title": "Orbit Board"}))

    fire_event(result.get_by_test_id("add-demo-task"), "click")
    assert "Preparar experimento de aquisição" in result.container.text_content
    assert result.get_by_test_id("stat-total").text_content == "Total4"
    assert result.get_by_test_id("stat-pendentes").text_content == "Pendentes3"

    fire_event(result.get_by_test_id("toggle-2"), "click")
    assert result.get_by_test_id("stat-concluídas").text_content == "Concluídas2"
    assert result.get_by_test_id("stat-progresso").text_content == "Progresso50%"
    cleanup()


def test_filters_and_delete_flow():
    result = render(h(App, {"title": "Orbit Board"}))

    fire_event(result.get_by_test_id("filter-done"), "click")
    assert "Revisar página inicial" in result.container.text_content
    assert "Definir métricas do onboarding" not in result.container.text_content

    fire_event(result.get_by_test_id("delete-1"), "click")
    assert "Nenhuma tarefa neste filtro." in result.container.text_content
    assert result.get_by_test_id("stat-total").text_content == "Total2"
    cleanup()


def test_presentational_component_supports_static_ssr():
    html = render_to_static_markup(
        h(StatCard, {"label": "Total", "value": 3, "tone": "info"})
    )

    assert 'class="stat-card stat-card--info"' in html
    assert "Total" in html
    assert "3" in html

