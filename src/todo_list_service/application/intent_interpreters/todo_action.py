from enum import StrEnum

from arclith.domain.ports.outbound.llm import LLMPort
from pydantic import BaseModel, Field


class TodoAction(StrEnum):
    CREATE_TODO = "create_todo"
    LIST_TODOS = "list_todos"
    CANCEL_TODO_CREATION = "cancel_todo_creation"
    UNKNOWN = "unknown"


class TodoActionDecision(BaseModel):
    action: TodoAction = Field(default=TodoAction.UNKNOWN)


class TodoActionInterpreter:
    def __init__(self, llm: LLMPort) -> None:
        self._llm = llm

    async def classify(self, prompt: str) -> TodoActionDecision:
        return await self._llm.complete_structured(
            prompt,
            output_type=TodoActionDecision,
            instructions=(
                "Tu classes l'intention d'un utilisateur qui parle a un agent de gestion de todos. "
                "Retourne create_todo quand il veut creer, ajouter ou enregistrer une tache. "
                "Retourne list_todos quand il veut afficher, lister ou consulter les taches existantes. "
                "Retourne cancel_todo_creation quand il annule une creation de todo en cours. "
                "Retourne unknown quand l'intention n'est pas une action todo prise en charge."
            ),
        )
