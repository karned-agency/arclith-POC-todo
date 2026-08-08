from __future__ import annotations

from weakref import WeakKeyDictionary

from arclith import Arclith
from arclith.domain.ports.outbound.repository import Repository

from todo_list_service.adapters.outbound.mongodb.repositories.todo_repository import MongoDBTodoRepository
from todo_list_service.application.use_cases.create_todo import CreateTodoUseCase
from todo_list_service.application.use_cases.list_todos import ListTodosUseCase
from todo_list_service.domain.models.todo import Todo
from todo_list_service.domain.ports.inbound.create_todo import CreateTodoPort
from todo_list_service.domain.ports.inbound.list_todos import ListTodosPort

_repositories: WeakKeyDictionary[Arclith, Repository[Todo]] = WeakKeyDictionary()


def build_todo_repository(app: Arclith) -> Repository[Todo]:
    repository = _repositories.get(app)
    if repository is None:
        repository = _create_todo_repository(app)
        _repositories[app] = repository
    return repository


def _create_todo_repository(app: Arclith) -> Repository[Todo]:
    if app.config.adapters.repository == "mongodb":
        return MongoDBTodoRepository(app.config.adapters.mongodb, app.logger)
    return app.repository(Todo)


def clear_todo_repository_cache() -> None:
    _repositories.clear()


def build_create_todo_use_case(app: Arclith) -> CreateTodoPort:
    return CreateTodoUseCase(build_todo_repository(app))


def build_list_todos_use_case(app: Arclith) -> ListTodosPort:
    return ListTodosUseCase(build_todo_repository(app))
