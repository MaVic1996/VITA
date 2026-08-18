from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

@dataclass
class Tool:
    name: str
    description: str
    function: Callable[..., Any]
    parameters: dict[str, Any]


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register_tool(self,tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        return self._tools[name]

    def all_tools(self) -> list[Tool]:
        return list(self._tools.values())