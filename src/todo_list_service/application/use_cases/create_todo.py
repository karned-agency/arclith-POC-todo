from __future__ import annotations

from datetime import datetime, timezone

from arclith.domain.ports.outbound.repository import Repository

from todo_list_service.domain.models.todo import Todo, TodoStatus
from todo_list_service.domain.ports.inbound.create_todo import CreateTodoCommand, CreateTodoPort


class CreateTodoUseCase(CreateTodoPort):
    def __init__(self, repository: Repository[Todo]) -> None:
        self._repository = repository

    async def execute(self, command: CreateTodoCommand) -> Todo:
        completed_at = command.completed_at
        if command.status == TodoStatus.DONE and completed_at is None:
            completed_at = datetime.now(timezone.utc)

        todo = Todo(
            title=command.title,
            description=command.description,
            due_date=command.due_date,
            status=command.status,
            completed_at=completed_at,
        )
        return await self._repository.create(todo)
