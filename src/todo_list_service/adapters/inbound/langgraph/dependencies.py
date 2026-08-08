from functools import lru_cache

from arclith import Arclith
from arclith.adapters.outbound.pydantic_ai.llm import PydanticAILLMAdapter
from arclith.domain.ports.outbound.llm import LLMPort

from todo_list_service.application.intent_interpreters.todo_action import TodoActionInterpreter
from todo_list_service.application.intent_interpreters.todo_conversation import TodoConversationInterpreter
from todo_list_service.domain.ports.inbound.create_todo import CreateTodoPort
from todo_list_service.domain.ports.inbound.list_todos import ListTodosPort
from todo_list_service.infrastructure.containers.todo_container import (
    build_create_todo_use_case,
    build_list_todos_use_case,
)

arclith = Arclith("config")


@lru_cache(maxsize=1)
def create_todo_use_case() -> CreateTodoPort:
    return build_create_todo_use_case(arclith)


@lru_cache(maxsize=1)
def list_todos_use_case() -> ListTodosPort:
    return build_list_todos_use_case(arclith)


@lru_cache(maxsize=1)
def llm_adapter() -> LLMPort:
    lm_settings = arclith.config.adapters.lm
    if lm_settings is None:
        raise RuntimeError("config/adapters/outbound/lm.yaml est requis pour l'agent.")
    return PydanticAILLMAdapter(lm_settings)


@lru_cache(maxsize=1)
def action_interpreter() -> TodoActionInterpreter:
    return TodoActionInterpreter(llm_adapter())


@lru_cache(maxsize=1)
def intent_interpreter() -> TodoConversationInterpreter:
    return TodoConversationInterpreter(llm_adapter())
