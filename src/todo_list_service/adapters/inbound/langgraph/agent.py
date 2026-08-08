from typing import Any

from arclith import Arclith
from langgraph.graph import END, START

from todo_list_service.adapters.inbound.langgraph.dependencies import (
    action_interpreter,
    arclith,
    create_todo_use_case,
    intent_interpreter,
    list_todos_use_case,
)
from todo_list_service.adapters.inbound.langgraph.nodes import (
    answer_unknown as answer_unknown_node,
    cancel_todo_creation as cancel_todo_creation_node,
    collect_todo_details as collect_todo_details_node,
    create_todo as create_todo_node,
    list_todos as list_todos_node,
    route_intent as route_intent_node,
)
from todo_list_service.adapters.inbound.langgraph.routing import (
    route_after_collection,
    route_after_intent,
)
from todo_list_service.adapters.inbound.langgraph.state import AgentState
from todo_list_service.application.intent_interpreters.todo_action import TodoActionInterpreter
from todo_list_service.application.intent_interpreters.todo_conversation import TodoConversationInterpreter
from todo_list_service.domain.ports.inbound.create_todo import CreateTodoPort
from todo_list_service.domain.ports.inbound.list_todos import ListTodosPort


def _create_todo_use_case() -> CreateTodoPort:
    return create_todo_use_case()


def _list_todos_use_case() -> ListTodosPort:
    return list_todos_use_case()


def _action_interpreter() -> TodoActionInterpreter:
    return action_interpreter()


def _intent_interpreter() -> TodoConversationInterpreter:
    return intent_interpreter()


def _route_after_intent(state: AgentState) -> str:
    return route_after_intent(state)


def _route_after_collection(state: AgentState) -> str:
    return route_after_collection(state)


async def route_intent(state: AgentState) -> AgentState:
    return await route_intent_node(state, _action_interpreter)


async def collect_todo_details(state: AgentState) -> AgentState:
    return await collect_todo_details_node(state, _intent_interpreter)


async def create_todo(state: AgentState) -> AgentState:
    return await create_todo_node(state, _create_todo_use_case)


async def list_todos(state: AgentState) -> AgentState:
    return await list_todos_node(state, _list_todos_use_case)


async def answer_unknown(state: AgentState) -> AgentState:
    return await answer_unknown_node(state)


async def cancel_todo_creation(state: AgentState) -> AgentState:
    return await cancel_todo_creation_node(state)


async def run_agent(state: AgentState) -> AgentState:
    return await agent.ainvoke(state)


def register_agent(builder: Any, app: Arclith) -> None:
    builder.add_node("route_intent", route_intent)
    builder.add_node("collect_todo_details", collect_todo_details)
    builder.add_node("create_todo", create_todo)
    builder.add_node("list_todos", list_todos)
    builder.add_node("answer_unknown", answer_unknown)
    builder.add_node("cancel_todo_creation", cancel_todo_creation)

    builder.add_edge(START, "route_intent")
    builder.add_conditional_edges(
        "route_intent",
        _route_after_intent,
        ["collect_todo_details", "list_todos", "cancel_todo_creation", "answer_unknown"],
    )
    builder.add_conditional_edges(
        "collect_todo_details",
        _route_after_collection,
        ["create_todo", END],
    )
    builder.add_edge("create_todo", END)
    builder.add_edge("list_todos", END)
    builder.add_edge("answer_unknown", END)
    builder.add_edge("cancel_todo_creation", END)


agent = arclith.langgraph(AgentState, register_agent, name="todo_agent")
