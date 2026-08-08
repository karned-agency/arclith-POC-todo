from typing import Any

from langgraph.graph import MessagesState

from todo_list_service.application.intent_interpreters.todo_action import TodoAction
from todo_list_service.application.intent_interpreters.todo_conversation import TodoDraft

type AgentAction = TodoAction


class AgentState(MessagesState, total=False):
    action: AgentAction
    draft: dict[str, Any]
    pending_field: str | None
    answer: str
    todos: list[dict[str, Any]]


def last_user_message(state: AgentState) -> str:
    for message in reversed(state.get("messages", [])):
        if message_role(message) in {"user", "human"}:
            return message_content(message)
    return ""


def message_role(message: Any) -> str | None:
    if isinstance(message, dict):
        role = message.get("role")
        return str(role) if role is not None else None

    role = getattr(message, "type", None)
    return str(role) if role is not None else None


def message_content(message: Any) -> str:
    if isinstance(message, dict):
        return str(message.get("content", ""))

    content = getattr(message, "content", "")
    return content if isinstance(content, str) else str(content)


def assistant_message(content: str) -> dict[str, str]:
    return {"role": "assistant", "content": content}


def draft_from_state(state: AgentState) -> TodoDraft:
    return TodoDraft.model_validate(state.get("draft", {}))
