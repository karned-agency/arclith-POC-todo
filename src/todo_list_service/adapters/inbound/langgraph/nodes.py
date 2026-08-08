from collections.abc import Callable

from pydantic import ValidationError

from todo_list_service.adapters.inbound.langgraph.collection import (
    apply_pending_answer,
    apply_default_fields,
    enrich_draft_from_prompt,
    missing_fields,
    question_for,
)
from todo_list_service.adapters.inbound.langgraph.formatters import format_todos, todo_to_agent_item
from todo_list_service.adapters.inbound.langgraph.intent import detect_high_confidence_action
from todo_list_service.adapters.inbound.langgraph.state import (
    AgentState,
    assistant_message,
    draft_from_state,
    last_user_message,
)
from todo_list_service.application.intent_interpreters.todo_action import TodoAction, TodoActionInterpreter
from todo_list_service.application.intent_interpreters.todo_conversation import TodoConversationInterpreter
from todo_list_service.domain.models.todo import TodoStatus
from todo_list_service.domain.ports.inbound.create_todo import CreateTodoCommand, CreateTodoPort
from todo_list_service.domain.ports.inbound.list_todos import ListTodosPort, ListTodosQuery

type CreateTodoUseCaseFactory = Callable[[], CreateTodoPort]
type ListTodosUseCaseFactory = Callable[[], ListTodosPort]
type ActionInterpreterFactory = Callable[[], TodoActionInterpreter]
type IntentInterpreterFactory = Callable[[], TodoConversationInterpreter]


async def route_intent(state: AgentState, get_action_interpreter: ActionInterpreterFactory) -> AgentState:
    prompt = last_user_message(state)
    local_action = detect_high_confidence_action(prompt, state)
    if local_action != TodoAction.UNKNOWN:
        return {"action": local_action}
    if not prompt.strip():
        return {"action": TodoAction.UNKNOWN}

    decision = await get_action_interpreter().classify(prompt)
    return {"action": decision.action}


async def collect_todo_details(state: AgentState, get_interpreter: IntentInterpreterFactory) -> AgentState:
    prompt = last_user_message(state)
    current = draft_from_state(state)
    pending_field = state.get("pending_field")

    if prompt:
        current, handled_pending = apply_pending_answer(prompt, current, pending_field)
        if not handled_pending:
            current = enrich_draft_from_prompt(prompt, current)
            missing_before_llm = missing_fields(apply_default_fields(current))
            if not missing_before_llm:
                return {
                    "draft": apply_default_fields(current).model_dump(mode="json", exclude_none=True),
                    "pending_field": None,
                }
            if pending_field:
                prompt = f"Le message utilisateur repond au champ {pending_field!r}: {prompt}"
            extracted = await get_interpreter().extract(prompt, current)
            current = current.model_copy(update=extracted.model_dump(exclude_none=True))
            current = enrich_draft_from_prompt(prompt, current)

    current = apply_default_fields(current)
    missing = missing_fields(current)
    if missing:
        pending_field = missing[0]
        answer = question_for(pending_field)
        return {
            "draft": current.model_dump(mode="json", exclude_none=True),
            "pending_field": pending_field,
            "answer": answer,
            "messages": [assistant_message(answer)],
        }

    return {
        "draft": current.model_dump(mode="json", exclude_none=True),
        "pending_field": None,
    }


async def cancel_todo_creation(state: AgentState) -> AgentState:
    answer = "Creation de todo annulee."
    return {
        "action": TodoAction.CANCEL_TODO_CREATION,
        "draft": {},
        "pending_field": None,
        "answer": answer,
        "messages": [assistant_message(answer)],
    }


async def create_todo(state: AgentState, get_create_use_case: CreateTodoUseCaseFactory) -> AgentState:
    current = draft_from_state(state)

    try:
        todo = await get_create_use_case().execute(
            CreateTodoCommand(
                title=current.title or "",
                description=current.description or "",
                due_date=current.due_date,
                status=current.status or TodoStatus.TODO,
                completed_at=current.completed_at,
            )
        )
    except (ValidationError, ValueError) as exc:
        answer = f"Je ne peux pas creer la todo: {exc}"
        return {
            "answer": answer,
            "messages": [assistant_message(answer)],
        }

    answer = f"Todo creee: {todo.title} ({todo.uuid})."
    return {
        "draft": {},
        "pending_field": None,
        "answer": answer,
        "messages": [assistant_message(answer)],
    }


async def list_todos(state: AgentState, get_list_use_case: ListTodosUseCaseFactory) -> AgentState:
    result = await get_list_use_case().execute(ListTodosQuery(page=1, per_page=20))
    answer = format_todos(result)
    return {
        "todos": [todo_to_agent_item(todo) for todo in result.items],
        "answer": answer,
        "messages": [assistant_message(answer)],
    }


async def answer_unknown(state: AgentState) -> AgentState:
    answer = "Je peux creer une todo ou lister les todos. Que veux-tu faire ?"
    return {
        "action": TodoAction.UNKNOWN,
        "answer": answer,
        "messages": [assistant_message(answer)],
    }
