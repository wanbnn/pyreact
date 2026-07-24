"""Metric card used by the Orbit project dashboard."""

from pyreact import h


def StatCard(props):
    """Render a labelled project metric."""
    return h(
        "article",
        {
            "className": f"stat-card stat-card--{props.get('tone', 'neutral')}",
            "data-testid": f"stat-{props['label'].lower()}",
        },
        h("span", {"className": "stat-card__label"}, props["label"]),
        h("strong", {"className": "stat-card__value"}, str(props["value"])),
    )

