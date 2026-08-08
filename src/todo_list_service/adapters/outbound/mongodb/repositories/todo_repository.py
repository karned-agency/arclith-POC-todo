from datetime import date
from typing import Any

from arclith.adapters.outbound.mongodb.config import MongoDBConfig
from arclith.adapters.outbound.mongodb.repository import MongoDBRepository
from arclith.domain.ports.outbound.logger import Logger
from todo_list_service.domain.models.todo import Todo


class MongoDBTodoRepository(MongoDBRepository[Todo]):
    def __init__(self, config: MongoDBConfig, logger: Logger) -> None:
        super().__init__(config, Todo, logger)

    def _to_doc(self, entity: Todo) -> dict[str, Any]:
        doc = super()._to_doc(entity)
        due_date = doc.get("due_date")
        if isinstance(due_date, date):
            doc["due_date"] = due_date.isoformat()
        return doc

    # TODO: add custom query methods here
    # async def find_by_name(self, name: str) -> list[Todo]:
    #     async with self._collection() as col:
    #         return [
    #             self._from_doc(doc)
    #             async for doc in col.find({"name": name, "deleted_at": None})
    #         ]
