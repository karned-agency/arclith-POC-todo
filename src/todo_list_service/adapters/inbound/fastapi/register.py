from __future__ import annotations

from arclith import Arclith
from fastapi import FastAPI

from todo_list_service.adapters.inbound.fastapi.handlers.todo_handlers import TodoHandlers
from todo_list_service.adapters.inbound.fastapi.routers.todo_router import build_todo_router
from todo_list_service.infrastructure.containers.todo_container import (
    build_create_todo_use_case,
    build_list_todos_use_case,
)


def register_routers(app: FastAPI, arclith: Arclith) -> None:
    create_todo = build_create_todo_use_case(arclith)
    list_todos = build_list_todos_use_case(arclith)
    handlers = TodoHandlers(create_todo, list_todos)
    app.include_router(build_todo_router(handlers))
