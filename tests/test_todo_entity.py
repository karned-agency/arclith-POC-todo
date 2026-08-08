from datetime import date, datetime, timezone

import pytest
from pydantic import ValidationError

from todo_list_service.domain.models.todo import Todo, TodoStatus


def test_create_todo_with_required_fields() -> None:
    todo = Todo(title="  Preparer la revue  ", due_date=date(2026, 8, 31))

    assert todo.title == "Preparer la revue"
    assert todo.description == ""
    assert todo.status == TodoStatus.TODO
    assert todo.completed_at is None


def test_done_requires_completed_at() -> None:
    with pytest.raises(ValidationError):
        Todo(title="Publier", due_date=date(2026, 8, 31), status=TodoStatus.DONE)


def test_completed_at_is_rejected_before_done() -> None:
    with pytest.raises(ValidationError):
        Todo(
            title="Publier",
            due_date=date(2026, 8, 31),
            completed_at=datetime.now(timezone.utc),
            status=TodoStatus.WIP,
        )
