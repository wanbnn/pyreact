"""Derived project metrics implemented as a reusable custom hook."""

from pyreact import use_memo


def use_task_stats(tasks):
    """Return total, completed, pending and completion percentage."""

    def calculate():
        total = len(tasks)
        completed = sum(1 for task in tasks if task["done"])
        pending = total - completed
        progress = round((completed / total) * 100) if total else 0
        return {
            "total": total,
            "completed": completed,
            "pending": pending,
            "progress": progress,
        }

    dependency = tuple((task["id"], task["done"]) for task in tasks)
    return use_memo(calculate, [dependency])

