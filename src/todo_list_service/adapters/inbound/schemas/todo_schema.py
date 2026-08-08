from __future__ import annotations

from datetime import date, datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field

from todo_list_service.domain.models.todo import TodoStatus


class TodoCreateSchema(BaseModel):
    model_config = ConfigDict(
        json_schema_extra={
            "examples": [
                {
                    "title": "Ecrire le tutoriel",
                    "description": "Couvrir API, MCP et agent",
                    "due_date": "2026-09-01",
                    "status": "todo",
                }
            ]
        }
    )

    title: str = Field(
        min_length=1,
        max_length=140,
        description="Titre court de la todo.",
        examples=["Ecrire le tutoriel"],
    )
    description: str = Field(
        default="",
        max_length=4000,
        description="Description detaillee.",
        examples=["Couvrir API, MCP et agent"],
    )
    due_date: date = Field(
        description="Date d'echeance au format ISO 8601.",
        examples=["2026-09-01"],
    )
    status: TodoStatus = Field(
        default=TodoStatus.TODO,
        description="Statut courant de la todo.",
        examples=["todo"],
    )
    completed_at: datetime | None = Field(
        default=None,
        description="Date de realisation, uniquement quand le statut est done.",
        examples=[None],
    )


class TodoCreatedSchema(BaseModel):
    uuid: UUID = Field(
        description="Identifiant public de la todo creee.",
        examples=["01951234-5678-7abc-def0-123456789abc"],
    )


class TodoSchema(BaseModel):
    model_config = ConfigDict(
        from_attributes=True,
        json_schema_extra={
            "examples": [
                {
                    "uuid": "01951234-5678-7abc-def0-123456789abc",
                    "title": "Ecrire le tutoriel",
                    "description": "Couvrir API, MCP et agent",
                    "due_date": "2026-09-01",
                    "completed_at": None,
                    "status": "todo",
                    "created_at": "2026-08-07T10:30:00Z",
                    "updated_at": "2026-08-07T10:30:00Z",
                    "version": 1,
                }
            ]
        },
    )

    uuid: UUID = Field(description="Identifiant public de la todo.")
    title: str = Field(description="Titre court.")
    description: str = Field(description="Description detaillee.")
    due_date: date = Field(description="Date d'echeance.")
    completed_at: datetime | None = Field(description="Date de realisation eventuelle.")
    status: TodoStatus = Field(description="Statut courant.")
    created_at: datetime = Field(description="Date de creation.")
    updated_at: datetime = Field(description="Date de derniere modification.")
    version: int = Field(description="Version metier utilisee par les mecanismes HTTP comme ETag.")
