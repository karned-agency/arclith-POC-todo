from datetime import date

import pytest
from arclith.adapters.outbound.memory.repository import InMemoryRepository

from todo_list_service.application.use_cases.create_todo import CreateTodoUseCase
from todo_list_service.application.use_cases.list_todos import ListTodosUseCase
from todo_list_service.domain.models.todo import Todo, TodoStatus
from todo_list_service.domain.ports.inbound.create_todo import CreateTodoCommand
from todo_list_service.domain.ports.inbound.list_todos import ListTodosQuery


@pytest.mark.asyncio
async def test_create_todo_persists_entity() -> None:
    repository = InMemoryRepository[Todo]()
    use_case = CreateTodoUseCase(repository)

    todo = await use_case.execute(
        CreateTodoCommand(
            title="Ecrire le tutoriel",
            description="Couvrir API, MCP et agent",
            due_date=date(2026, 9, 1),
        )
    )

    assert todo.status == TodoStatus.TODO
    assert await repository.read(todo.uuid) == todo


@pytest.mark.asyncio
async def test_done_todo_gets_completion_date() -> None:
    repository = InMemoryRepository[Todo]()
    use_case = CreateTodoUseCase(repository)

    todo = await use_case.execute(
        CreateTodoCommand(
            title="Publier",
            due_date=date(2026, 9, 1),
            status=TodoStatus.DONE,
        )
    )

    assert todo.completed_at is not None


@pytest.mark.asyncio
async def test_list_todos_returns_persisted_entities() -> None:
    repository = InMemoryRepository[Todo]()
    create_todo = CreateTodoUseCase(repository)
    list_todos = ListTodosUseCase(repository)

    todo = await create_todo.execute(
        CreateTodoCommand(
            title="Tester le listing",
            due_date=date(2026, 9, 1),
        )
    )

    result = await list_todos.execute(ListTodosQuery())

    assert result.items == [todo]
    assert result.total == 1
    assert result.page == 1
    assert result.per_page == 20
