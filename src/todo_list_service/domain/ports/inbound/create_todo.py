from __future__ import annotations

from abc import ABC, abstractmethod
from datetime import date, datetime

from pydantic import BaseModel, Field

from todo_list_service.domain.models.todo import Todo, TodoStatus


class CreateTodoCommand(BaseModel):
    title: str = Field(min_length=1, max_length=140)
    description: str = Field(default="", max_length=4000)
    due_date: date
    status: TodoStatus = TodoStatus.TODO
    completed_at: datetime | None = None


class CreateTodoPort(ABC):
    @abstractmethod
    async def execute(self, command: CreateTodoCommand) -> Todo:
        raise NotImplementedError
