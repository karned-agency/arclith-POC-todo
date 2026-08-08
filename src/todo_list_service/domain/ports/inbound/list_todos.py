from __future__ import annotations

from abc import ABC, abstractmethod

from pydantic import BaseModel, Field

from todo_list_service.domain.models.todo import Todo


class ListTodosQuery(BaseModel):
    page: int = Field(default=1, ge=1)
    per_page: int = Field(default=20, ge=1, le=100)


class ListTodosResult(BaseModel):
    items: list[Todo]
    total: int = Field(ge=0)
    page: int = Field(ge=1)
    per_page: int = Field(ge=1, le=100)


class ListTodosPort(ABC):
    @abstractmethod
    async def execute(self, query: ListTodosQuery) -> ListTodosResult:
        raise NotImplementedError
