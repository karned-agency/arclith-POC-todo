from __future__ import annotations

from arclith.adapters.inbound.schemas import ApiResponse, PaginatedResponse
from fastapi import APIRouter

from todo_list_service.adapters.inbound.fastapi.handlers.todo_handlers import TodoHandlers
from todo_list_service.adapters.inbound.schemas.todo_schema import TodoCreatedSchema, TodoSchema

_CREATED_TODO_EXAMPLE = {
    "status": "success",
    "data": {"uuid": "01951234-5678-7abc-def0-123456789abc"},
    "metadata": {
        "request_id": "01951234-5678-7abc-def0-123456789abc",
        "timestamp": "2026-08-07T10:30:00Z",
        "version": "v1",
        "links": {
            "self": "/v1/todos/01951234-5678-7abc-def0-123456789abc",
            "collection": "/v1/todos",
        },
    },
}

_FULL_TODO_EXAMPLE = {
    "status": "success",
    "data": {
        "uuid": "01951234-5678-7abc-def0-123456789abc",
        "title": "Ecrire le tutoriel",
        "description": "Couvrir API, MCP et agent",
        "due_date": "2026-09-01",
        "completed_at": None,
        "status": "todo",
        "created_at": "2026-08-07T10:30:00Z",
        "updated_at": "2026-08-07T10:30:00Z",
        "version": 1,
    },
    "metadata": _CREATED_TODO_EXAMPLE["metadata"],
}

_TODO_LIST_EXAMPLE = {
    "status": "success",
    "data": [_FULL_TODO_EXAMPLE["data"]],
    "pagination": {
        "total": 1,
        "page": 1,
        "per_page": 20,
        "pages": 1,
        "has_next": False,
        "has_prev": False,
        "next_page": None,
        "prev_page": None,
    },
    "metadata": {
        "request_id": "01951234-5678-7abc-def0-123456789abc",
        "timestamp": "2026-08-07T10:30:00Z",
        "version": "v1",
        "links": {"self": "/v1/todos"},
    },
}

_VALIDATION_ERROR_RESPONSE = {
    "description": "Payload ou parametres invalides.",
    "content": {
        "application/json": {
            "example": {
                "detail": [
                    {
                        "type": "greater_than_equal",
                        "loc": ["query", "page"],
                        "msg": "Input should be greater than or equal to 1",
                        "input": 0,
                        "ctx": {"ge": 1},
                    }
                ]
            }
        }
    },
}

_BAD_REQUEST_RESPONSE = {
    "description": "Requete invalide avant execution du use case.",
    "content": {
        "application/json": {
            "example": {
                "detail": "Idempotency-Key exceeds 255 characters",
            }
        }
    },
}

_CREATE_TODO_RESPONSES = {
    201: {
        "description": "Todo creee. La reponse minimale contient l'UUID.",
        "headers": {
            "Location": {
                "description": "URL canonique de la todo creee.",
                "schema": {"type": "string"},
            },
            "Link": {
                "description": "Liens HATEOAS self et collection.",
                "schema": {"type": "string"},
            },
            "X-Idempotency-Replay": {
                "description": "Present a true si la reponse vient du cache d'idempotence.",
                "schema": {"type": "boolean"},
            },
        },
        "content": {
            "application/json": {
                "examples": {
                    "minimal": {"summary": "Reponse par defaut", "value": _CREATED_TODO_EXAMPLE},
                    "representation": {
                        "summary": "Avec Prefer: return=representation",
                        "value": _FULL_TODO_EXAMPLE,
                    },
                }
            }
        },
    },
    400: _BAD_REQUEST_RESPONSE,
    422: _VALIDATION_ERROR_RESPONSE,
}

_LIST_TODOS_RESPONSES = {
    200: {
        "description": "Page de todos actives.",
        "headers": {
            "X-Total-Count": {
                "description": "Nombre total de todos actives avant pagination.",
                "schema": {"type": "integer"},
            },
            "Link": {
                "description": "Lien HATEOAS vers la collection.",
                "schema": {"type": "string"},
            },
        },
        "content": {"application/json": {"example": _TODO_LIST_EXAMPLE}},
    },
    422: _VALIDATION_ERROR_RESPONSE,
}


def build_todo_router(handlers: TodoHandlers) -> APIRouter:
    router = APIRouter(prefix="/v1/todos", tags=["todos"])
    router.add_api_route(
        "/",
        handlers.create_todo,
        methods=["POST"],
        response_model=ApiResponse[TodoCreatedSchema | TodoSchema],
        response_model_exclude_none=True,
        status_code=201,
        summary="Creer une todo",
        description="Cree une todo via CreateTodoPort, sans acces direct au repository.",
        response_description="Todo creee dans l'enveloppe de reponse Arclith.",
        operation_id="createTodo",
        responses=_CREATE_TODO_RESPONSES,
    )
    router.add_api_route(
        "/",
        handlers.list_todos,
        methods=["GET"],
        response_model=PaginatedResponse[TodoSchema],
        response_model_exclude_none=True,
        status_code=200,
        summary="Lister les todos",
        description="Retourne une page de todos via ListTodosPort, sans acces direct au repository.",
        response_description="Page de todos dans l'enveloppe paginee Arclith.",
        operation_id="listTodos",
        responses=_LIST_TODOS_RESPONSES,
    )
    return router
