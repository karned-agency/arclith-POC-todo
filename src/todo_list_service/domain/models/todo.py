from __future__ import annotations

from datetime import date, datetime
from enum import StrEnum

from arclith.domain.models.entity import Entity
from pydantic import Field, field_validator, model_validator


class TodoStatus(StrEnum):
    TODO = "todo"
    WIP = "wip"
    DONE = "done"


class Todo(Entity):
    title: str = Field(min_length=1, max_length=140)
    description: str = Field(default="", max_length=4000)
    due_date: date
    completed_at: datetime | None = None
    status: TodoStatus = TodoStatus.TODO

    @field_validator("title")
    @classmethod
    def normalize_title(cls, value: str) -> str:
        normalized = value.strip()
        if not normalized:
            raise ValueError("title ne peut pas etre vide")
        return normalized

    @field_validator("description")
    @classmethod
    def normalize_description(cls, value: str) -> str:
        return value.strip()

    @model_validator(mode="after")
    def validate_completion(self) -> "Todo":
        if self.status == TodoStatus.DONE and self.completed_at is None:
            raise ValueError("completed_at est requis quand status=done")
        if self.status != TodoStatus.DONE and self.completed_at is not None:
            raise ValueError("completed_at doit rester vide tant que la todo n'est pas done")
        return self
