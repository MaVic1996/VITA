from collections.abc import Callable

from pydantic import BaseModel

from vita.agent.agent import Agent
from vita.memory.sqlite import SQLitePreferencesRepository
from vita.tools.registry import Tool, ToolRegistry


class DeleteEventArgs(BaseModel):
    event_id: str


class FakeLLMClient:
    def chat(self, messages: list[dict], tools: list[dict]) -> dict:
        return {
            "role": "assistant",
            "content": "",
            "tool_calls": [
                {
                    "function": {
                        "name": "calendar_delete_event",
                        "arguments": {"event_id": "event-123"},
                    }
                }
            ],
        }


def build_agent(
    tmp_path, delete_event: Callable[[str], str]
) -> Agent:
    tools = ToolRegistry()
    tools.register_tool(
        Tool(
            name="calendar_delete_event",
            description="Delete a calendar event.",
            function=delete_event,
            args_model=DeleteEventArgs,
            requires_confirmation=True,
            confirmation_message="Voy a eliminar el evento seleccionado.",
        )
    )

    repository = SQLitePreferencesRepository(tmp_path / "vita.db")
    return Agent(FakeLLMClient(), tools, repository)


def test_rejected_action_is_not_executed(tmp_path) -> None:
    calls: list[str] = []
    agent = build_agent(tmp_path, lambda event_id: calls.append(event_id) or "deleted")

    agent.chat("Elimina la actividad")
    response = agent.chat("no")

    assert calls == []
    assert response == "Se ha cancelado la acción"


def test_confirmed_action_is_executed_once_with_saved_arguments(tmp_path) -> None:
    calls: list[str] = []
    agent = build_agent(tmp_path, lambda event_id: calls.append(event_id) or "deleted")

    agent.chat("Elimina la actividad")
    response = agent.chat("sí")

    assert calls == ["event-123"]
    assert response == "Se ha ejecutado la acción."
