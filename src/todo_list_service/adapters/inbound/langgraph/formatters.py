from typing import Any

from todo_list_service.domain.models.todo import Todo
from todo_list_service.domain.ports.inbound.list_todos import ListTodosResult


def todo_to_agent_item(todo: Todo) -> dict[str, Any]:
    return todo.model_dump(mode="json")


def format_todos(result: ListTodosResult) -> str:
    if result.total == 0:
        return "Aucune todo pour le moment."

    lines = [f"Voici {len(result.items)} todo(s) sur {result.total}:"]
    lines.extend(format_todo_line(todo) for todo in result.items)
    return "\n".join(lines)


def format_todo_line(todo: Todo) -> str:
    description = f" - {todo.description}" if todo.description else ""
    return (
        f"- {todo.title} [{todo.status.value}] "
        f"pour le {todo.due_date.isoformat()}{description} ({todo.uuid})"
    )
