from __future__ import annotations

import fastmcp
from arclith import Arclith

from todo_list_service.adapters.inbound.fastmcp.tools import TodoMCP
from todo_list_service.infrastructure.containers.todo_container import (
    build_create_todo_use_case,
    build_list_todos_use_case,
)


def register_tools(mcp: fastmcp.FastMCP, arclith: Arclith) -> None:
    create_todo = build_create_todo_use_case(arclith)
    list_todos = build_list_todos_use_case(arclith)
    TodoMCP(create_todo, list_todos, mcp)
