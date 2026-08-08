from collections.abc import Iterator
from pathlib import Path
import shutil

import pytest

from todo_list_service.infrastructure.containers.todo_container import clear_todo_repository_cache

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_RUNTIME_CONFIG = _PROJECT_ROOT / "config"


@pytest.fixture
def memory_config(tmp_path: Path) -> Path:
    config_dir = tmp_path / "config"
    shutil.copytree(_RUNTIME_CONFIG, config_dir)
    (config_dir / "adapters" / "adapters.yaml").write_text(
        "logger: console\n"
        "repository: memory\n"
        "observability:\n"
        "  enabled: []\n",
        encoding="utf-8",
    )
    return config_dir


@pytest.fixture(autouse=True)
def reset_todo_repository_cache() -> Iterator[None]:
    clear_todo_repository_cache()
    yield
    clear_todo_repository_cache()
