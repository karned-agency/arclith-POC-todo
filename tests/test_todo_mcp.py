from pathlib import Path

import pytest
from fastmcp import Client

from main import build_mcp


@pytest.mark.asyncio
async def test_mcp_create_and_list_todos(memory_config: Path) -> None:
    async with Client(build_mcp(memory_config)) as client:
        tools = await client.list_tools()
        assert {tool.name for tool in tools} >= {"create_todo_item", "list_todo_items"}

        result = await client.call_tool(
            "create_todo_item",
            {
                "title": "Tester le MCP",
                "description": "Appeler le meme use case que l'API",
                "due_date": "2026-09-01",
                "status": "todo",
            },
        )

        assert not result.is_error
        assert isinstance(result.structured_content, dict)

        listed = await client.call_tool("list_todo_items", {})
        assert not listed.is_error
        assert isinstance(listed.structured_content, dict)
        assert listed.structured_content["result"] == [result.structured_content]
