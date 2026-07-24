"""Orbit Board: a realistic PyReact project-management example."""

from pyreact import h, render, use_memo, use_state

from src.components import StatCard, TaskCard
from src.hooks import use_task_stats


INITIAL_TASKS = [
    {
        "id": 1,
        "project": "Website",
        "title": "Revisar página inicial",
        "description": "Validar conteúdo, contraste e comportamento responsivo.",
        "done": True,
    },
    {
        "id": 2,
        "project": "Produto",
        "title": "Definir métricas do onboarding",
        "description": "Selecionar os eventos que medem ativação e retenção.",
        "done": False,
    },
    {
        "id": 3,
        "project": "Operações",
        "title": "Automatizar relatório semanal",
        "description": "Consolidar indicadores e publicar o resumo da equipe.",
        "done": False,
    },
]


def App(props):
    """Main application with state, derived data and reusable components."""
    tasks, set_tasks = use_state(lambda: [task.copy() for task in INITIAL_TASKS])
    active_filter, set_active_filter = use_state("all")
    stats = use_task_stats(tasks)

    visible_tasks = use_memo(
        lambda: [
            task
            for task in tasks
            if active_filter == "all"
            or (active_filter == "done" and task["done"])
            or (active_filter == "pending" and not task["done"])
        ],
        [tuple((task["id"], task["done"]) for task in tasks), active_filter],
    )

    def toggle_task(task_id):
        set_tasks(
            lambda current: [
                {**task, "done": not task["done"]} if task["id"] == task_id else task
                for task in current
            ]
        )

    def delete_task(task_id):
        set_tasks(lambda current: [task for task in current if task["id"] != task_id])

    def add_demo_task(_event=None):
        set_tasks(
            lambda current: [
                *current,
                {
                    "id": max((task["id"] for task in current), default=0) + 1,
                    "project": "Crescimento",
                    "title": "Preparar experimento de aquisição",
                    "description": "Documentar hipótese, público e critério de sucesso.",
                    "done": False,
                },
            ]
        )

    return h(
        "main",
        {"className": "orbit-shell"},
        h(
            "header",
            {"className": "hero"},
            h("span", {"className": "eyebrow"}, "PYREACT EM PRODUÇÃO"),
            h("h1", None, props.get("title", "Orbit Board")),
            h(
                "p",
                None,
                "Um painel de execução para transformar prioridades em entregas.",
            ),
            h(
                "button",
                {
                    "type": "button",
                    "data-testid": "add-demo-task",
                    "onClick": add_demo_task,
                },
                "Adicionar tarefa exemplo",
            ),
        ),
        h(
            "section",
            {"className": "stats", "aria-label": "Resumo do projeto"},
            h(StatCard, {"label": "Total", "value": stats["total"]}),
            h(
                StatCard,
                {"label": "Pendentes", "value": stats["pending"], "tone": "warning"},
            ),
            h(
                StatCard,
                {"label": "Concluídas", "value": stats["completed"], "tone": "success"},
            ),
            h(
                StatCard,
                {"label": "Progresso", "value": f"{stats['progress']}%", "tone": "info"},
            ),
        ),
        h(
            "nav",
            {"className": "filters", "aria-label": "Filtros de tarefas"},
            *[
                h(
                    "button",
                    {
                        "type": "button",
                        "data-testid": f"filter-{filter_name}",
                        "aria-pressed": active_filter == filter_name,
                        "onClick": lambda _, value=filter_name: set_active_filter(value),
                    },
                    label,
                )
                for filter_name, label in (
                    ("all", "Todas"),
                    ("pending", "Pendentes"),
                    ("done", "Concluídas"),
                )
            ],
        ),
        h(
            "section",
            {"className": "task-list", "aria-label": "Tarefas"},
            *[
                h(
                    TaskCard,
                    {
                        "key": task["id"],
                        "task": task,
                        "onToggle": toggle_task,
                        "onDelete": delete_task,
                    },
                )
                for task in visible_tasks
            ],
            *(
                []
                if visible_tasks
                else [h("p", {"className": "empty-state"}, "Nenhuma tarefa neste filtro.")]
            ),
        ),
    )


if __name__ == "__main__":
    from pyreact.dom.dom_operations import document

    root = document.create_element("div")
    root.attributes["id"] = "root"
    document.body.append_child(root)
    render(h(App, {"title": "Orbit Board"}), root)

