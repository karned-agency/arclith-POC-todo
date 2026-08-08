from pathlib import Path

from arclith import Arclith


def test_project_config_loads(memory_config: Path) -> None:
    app = Arclith(memory_config)

    assert app.config.app.name
    assert app.config.adapters.repository == "memory"


def test_package_imports() -> None:
    import todo_list_service

    assert todo_list_service.__name__ == "todo_list_service"
