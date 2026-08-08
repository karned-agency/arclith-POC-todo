"""Application entrypoint for todo-list-service."""
from __future__ import annotations

import os
import sys
from pathlib import Path

import fastmcp
from arclith import Arclith

from todo_list_service.adapters.inbound.fastapi.register import register_routers
from todo_list_service.adapters.inbound.fastmcp.register import register_tools

_DEFAULT_CONFIG = Path(__file__).parent / "config"
_CONFIG = Path(os.getenv("TODO_LIST_CONFIG_DIR", str(_DEFAULT_CONFIG)))
_VALID_MODES = {"api", "mcp_http", "all"}

MODE = os.getenv("MODE", "api")
if MODE not in _VALID_MODES:
    print(f"MODE invalide: {MODE!r}. Valeurs: {sorted(_VALID_MODES)}", file=sys.stderr)
    sys.exit(1)

arclith = Arclith(_CONFIG)

app = arclith.fastapi()
register_routers(app, arclith)


def build_mcp(config_dir: Path | str | None = None) -> fastmcp.FastMCP:
    current_arclith = arclith if config_dir is None else Arclith(Path(config_dir))
    mcp = current_arclith.fastmcp("Todo MCP")
    register_tools(mcp, current_arclith)
    current_arclith.instrument_mcp(mcp)
    return mcp


def _run_api() -> None:
    arclith.run_api("main:app")


def _run_mcp_http() -> None:
    arclith.run_mcp_http(build_mcp())


if __name__ == "__main__":
    match MODE:
        case "api":
            arclith.run_with_probes(_run_api, transports=["api"])
        case "mcp_http":
            arclith.run_with_probes(_run_mcp_http, transports=["mcp_http"])
        case "all":
            arclith.run_with_probes(_run_api, _run_mcp_http, transports=["api", "mcp_http"])
