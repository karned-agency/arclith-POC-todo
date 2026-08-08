from datetime import date, datetime

from todo_list_service.adapters.inbound.langgraph.parsing import extract_title_hint, parse_relative_due_date, parse_status
from todo_list_service.application.intent_interpreters.todo_conversation import TodoDraft
from todo_list_service.domain.models.todo import TodoStatus


def enrich_draft_from_prompt(prompt: str, current: TodoDraft) -> TodoDraft:
    updates: dict[str, object] = {}
    if not current.title:
        title = extract_title_hint(prompt)
        if title is not None:
            updates["title"] = title

    if current.due_date is None:
        due_date = parse_relative_due_date(prompt)
        if due_date is not None:
            updates["due_date"] = due_date

    return current.model_copy(update=updates) if updates else current


def apply_default_fields(draft: TodoDraft) -> TodoDraft:
    updates: dict[str, object] = {}
    if draft.description is None:
        updates["description"] = ""
    if draft.status is None:
        updates["status"] = TodoStatus.TODO
    return draft.model_copy(update=updates) if updates else draft


def apply_pending_answer(prompt: str, current: TodoDraft, pending_field: str | None) -> tuple[TodoDraft, bool]:
    answer = prompt.strip()
    if not answer or pending_field is None:
        return current, False

    match pending_field:
        case "title":
            return current.model_copy(update={"title": answer}), True
        case "description":
            return current.model_copy(update={"description": answer}), True
        case "status":
            status = parse_status(answer)
            if status is None:
                return current, False
            return current.model_copy(update={"status": status}), True
        case "due_date":
            try:
                return current.model_copy(update={"due_date": date.fromisoformat(answer)}), True
            except ValueError:
                return current, False
        case "completed_at":
            try:
                return current.model_copy(update={"completed_at": datetime.fromisoformat(answer)}), True
            except ValueError:
                return current, False
        case _:
            return current, False


def missing_fields(draft: TodoDraft) -> list[str]:
    missing: list[str] = []
    if not draft.title:
        missing.append("title")
    if draft.due_date is None:
        missing.append("due_date")
    if draft.status == TodoStatus.DONE and draft.completed_at is None:
        missing.append("completed_at")
    return missing


def question_for(field: str) -> str:
    questions = {
        "title": "Quel est le titre de la todo ?",
        "due_date": "Quelle est la date d'echeance ?",
        "completed_at": "Quelle est la date de realisation ?",
    }
    return questions[field]
