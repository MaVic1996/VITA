from datetime import UTC, datetime

from vita.memory.conversation.models import ConversationMessage
from vita.memory.conversation.sqlite import SQLiteConversationRepository


def test_save_assigns_an_id_and_restores_messages_in_chronological_order(
    tmp_path,
) -> None:
    repository = SQLiteConversationRepository(tmp_path / "vita.db")

    first = repository.save(
        ConversationMessage(
            role="user",
            content="Buenos días",
            created_at=datetime(2026, 9, 19, 9, 0, tzinfo=UTC),
        )
    )
    second = repository.save(
        ConversationMessage(
            role="assistant",
            content="Buenos días, Víctor.",
            created_at=datetime(2026, 9, 19, 9, 1, tzinfo=UTC),
        )
    )
    third = repository.save(
        ConversationMessage(
            role="user",
            content="¿Qué tengo hoy?",
            created_at=datetime(2026, 9, 19, 9, 2, tzinfo=UTC),
        )
    )

    messages = repository.get_last_messages(limit=2)

    assert first.id == 1
    assert messages == [second, third]
