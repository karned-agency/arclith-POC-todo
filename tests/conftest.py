from collections.abc import Iterator
import os
from pathlib import Path
import shutil
from tempfile import TemporaryDirectory

import pytest

from todo_list_service.infrastructure.containers.todo_container import clear_todo_repository_cache

_PROJECT_ROOT = Path(__file__).resolve().parents[1]
_RUNTIME_CONFIG = _PROJECT_ROOT / "config"
_ORIGINAL_CONFIG_DIR = os.environ.get("TODO_LIST_CONFIG_DIR")
_SESSION_CONFIG: TemporaryDirectory[str] | None = None


def _copy_memory_config(destination: Path) -> Path:
    config_dir = destination / "config"
    shutil.copytree(_RUNTIME_CONFIG, config_dir)
    (config_dir / "adapters" / "adapters.yaml").write_text(
        "logger: console\n"
        "repository: memory\n"
        "observability:\n"
        "  enabled: []\n",
        encoding="utf-8",
    )
    return config_dir


def pytest_configure() -> None:
    global _SESSION_CONFIG
    _SESSION_CONFIG = TemporaryDirectory(prefix="arclith-poc-tests-")
    config_dir = _copy_memory_config(Path(_SESSION_CONFIG.name))
    os.environ["TODO_LIST_CONFIG_DIR"] = str(config_dir)


def pytest_unconfigure() -> None:
    global _SESSION_CONFIG
    if _ORIGINAL_CONFIG_DIR is None:
        os.environ.pop("TODO_LIST_CONFIG_DIR", None)
    else:
        os.environ["TODO_LIST_CONFIG_DIR"] = _ORIGINAL_CONFIG_DIR
    if _SESSION_CONFIG is not None:
        _SESSION_CONFIG.cleanup()
        _SESSION_CONFIG = None


@pytest.fixture
def memory_config(tmp_path: Path) -> Path:
    return _copy_memory_config(tmp_path)


@pytest.fixture(autouse=True)
def reset_todo_repository_cache() -> Iterator[None]:
    clear_todo_repository_cache()
    yield
    clear_todo_repository_cache()
