from todo_list_service.adapters.inbound.langgraph.parsing import is_cancel_request, normalize_user_text
from todo_list_service.adapters.inbound.langgraph.state import AgentAction, AgentState
from todo_list_service.application.intent_interpreters.todo_action import TodoAction

LIST_INTENT_MARKERS = (
    "affiche",
    "lister",
    "liste",
    "montre",
    "voir",
    "recap",
)
LIST_QUESTION_MARKERS = (
    "qu est ce que je dois faire",
    "que dois je faire",
    "quoi faire",
    "ce que je dois faire",
)
TODO_TARGET_MARKERS = (
    "todo",
    "todos",
    "tache",
    "taches",
)
CREATE_INTENT_MARKERS = (
    "ajoute",
    "ajouter",
    "cree",
    "creer",
    "nouvelle",
    "nouveau",
    "pense a",
    "rappelle",
)
CREATE_PREFIX_MARKERS = (
    "je dois",
    "j ai besoin de",
    "il faut",
    "il faut que je",
)


def has_intent_marker(normalized: str, markers: tuple[str, ...]) -> bool:
    words = set(normalized.split())
    for marker in markers:
        if " " in marker:
            if marker in normalized:
                return True
        elif marker in words:
            return True
    return False


def has_prefix_marker(normalized: str, markers: tuple[str, ...]) -> bool:
    return any(normalized == marker or normalized.startswith(f"{marker} ") for marker in markers)


def detect_high_confidence_action(prompt: str, state: AgentState) -> AgentAction:
    has_todo_draft = bool(state.get("pending_field") or state.get("draft"))
    if has_todo_draft and is_cancel_request(prompt):
        return TodoAction.CANCEL_TODO_CREATION
    if state.get("pending_field") or state.get("draft"):
        return TodoAction.CREATE_TODO

    normalized = normalize_user_text(prompt)
    targets_todo_domain = has_intent_marker(normalized, TODO_TARGET_MARKERS)
    if has_intent_marker(normalized, LIST_QUESTION_MARKERS):
        return TodoAction.LIST_TODOS
    if has_intent_marker(normalized, LIST_INTENT_MARKERS) and targets_todo_domain:
        return TodoAction.LIST_TODOS
    if has_prefix_marker(normalized, CREATE_PREFIX_MARKERS):
        return TodoAction.CREATE_TODO
    if has_intent_marker(normalized, CREATE_INTENT_MARKERS):
        return TodoAction.CREATE_TODO
    return TodoAction.UNKNOWN
