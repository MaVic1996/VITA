from datetime import UTC, datetime, timedelta
from typing import Any

from vita.agent.agent import Agent
from vita.memory.conversation.models import ConversationMessage
from vita.memory.conversation.sqlite import SQLiteConversationRepository
from vita.memory.preferences.sqlite import SQLitePreferencesRepository
from vita.tools.registry import ToolRegistry


class FakeLLMClient:
    def __init__(self) -> None:
        self.received_messages: list[dict[str, Any]] = []

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]],
    ) -> dict[str, Any]:
        self.received_messages = [message.copy() for message in messages]
        return {"role": "assistant", "content": "No tienes eventos hoy."}


def test_agent_loads_history_and_persists_the_new_exchange(tmp_path) -> None:
    database_path = tmp_path / "vita.db"
    conversation_repository = SQLiteConversationRepository(database_path)
    now = datetime.now(UTC)
    conversation_repository.save(
        ConversationMessage(
            role="user",
            content="Hola",
            created_at=now - timedelta(minutes=2),
        )
    )
    conversation_repository.save(
        ConversationMessage(
            role="assistant",
            content="Hola, Víctor.",
            created_at=now - timedelta(minutes=1),
        )
    )
    llm_client = FakeLLMClient()
    agent = Agent(
        llm_client=llm_client,
        tools=ToolRegistry(),
        preferences_repository=SQLitePreferencesRepository(database_path),
        conversation_repository=conversation_repository,
    )

    response = agent.chat("¿Qué tengo hoy?")

    assert response == "No tienes eventos hoy."
    assert llm_client.received_messages[1:3] == [
        {"role": "user", "content": "Hola"},
        {"role": "assistant", "content": "Hola, Víctor."},
    ]
    assert llm_client.received_messages[3]["role"] == "user"
    assert llm_client.received_messages[3]["content"].startswith("¿Qué tengo hoy?")
    assert [message.content for message in conversation_repository.get_last_messages()] == [
        "Hola",
        "Hola, Víctor.",
        "¿Qué tengo hoy?",
        "No tienes eventos hoy.",
    ]
