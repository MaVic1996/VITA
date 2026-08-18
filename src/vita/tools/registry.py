from collections.abc import Callable
from dataclasses import dataclass
from typing import Any
from pydantic import BaseModel

@dataclass
class Tool:
    name: str
    description: str
    function: Callable[..., Any]
    args_model: type[BaseModel]

    def definition(self) -> dict[str, Any]:
        return {
            "type": "function",
            "function": {
                "name": self.name,
                "description": self.description,
                "parameters": self.args_model.model_json_schema(),
            }
        }


class ToolRegistry:
    def __init__(self):
        self._tools: dict[str, Tool] = {}

    def register_tool(self,tool: Tool) -> None:
        self._tools[tool.name] = tool

    def get_tool(self, name: str) -> Tool:
        return self._tools[name]

    def all_tools(self) -> list[Tool]:
        return list(self._tools.values())