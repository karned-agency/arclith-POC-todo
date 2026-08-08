from langgraph.graph import END

from todo_list_service.adapters.inbound.langgraph.state import AgentState
from todo_list_service.application.intent_interpreters.todo_action import TodoAction


def route_after_intent(state: AgentState) -> str:
    action = state.get("action", TodoAction.UNKNOWN)
    if action == TodoAction.LIST_TODOS:
        return "list_todos"
    if action == TodoAction.CANCEL_TODO_CREATION:
        return "cancel_todo_creation"
    if action == TodoAction.CREATE_TODO:
        return "collect_todo_details"
    return "answer_unknown"


def route_after_collection(state: AgentState) -> str:
    if state.get("pending_field") is not None:
        return END
    return "create_todo"
