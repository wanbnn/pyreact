"""Task card used by the Orbit project dashboard."""

from pyreact import h


def TaskCard(props):
    """Render one actionable task."""
    task = props["task"]
    status = "Concluída" if task["done"] else "Em andamento"
    return h(
        "article",
        {
            "className": f"task-card{' task-card--done' if task['done'] else ''}",
            "data-testid": f"task-{task['id']}",
        },
        h(
            "div",
            {"className": "task-card__content"},
            h("span", {"className": "task-card__project"}, task["project"]),
            h("h3", None, task["title"]),
            h("p", None, task["description"]),
            h("span", {"className": "task-card__status"}, status),
        ),
        h(
            "div",
            {"className": "task-card__actions"},
            h(
                "button",
                {
                    "type": "button",
                    "data-testid": f"toggle-{task['id']}",
                    "onClick": lambda _: props["onToggle"](task["id"]),
                },
                "Reabrir" if task["done"] else "Concluir",
            ),
            h(
                "button",
                {
                    "type": "button",
                    "data-testid": f"delete-{task['id']}",
                    "onClick": lambda _: props["onDelete"](task["id"]),
                },
                "Excluir",
            ),
        ),
    )

