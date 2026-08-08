from __future__ import annotations

from arclith.domain.ports.outbound.repository import Repository

from todo_list_service.domain.models.todo import Todo
from todo_list_service.domain.ports.inbound.list_todos import (
    ListTodosPort,
    ListTodosQuery,
    ListTodosResult,
)


class ListTodosUseCase(ListTodosPort):
    def __init__(self, repository: Repository[Todo]) -> None:
        self._repository = repository

    async def execute(self, query: ListTodosQuery) -> ListTodosResult:
        offset = (query.page - 1) * query.per_page
        items, total = await self._repository.find_page(offset=offset, limit=query.per_page)
        return ListTodosResult(
            items=items,
            total=total,
            page=query.page,
            per_page=query.per_page,
        )
