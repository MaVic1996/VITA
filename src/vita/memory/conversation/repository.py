
from typing import Protocol

from vita.memory.conversation.models import ConversationMessage


class ConversationRepository(Protocol):
    """Repository for managing conversation messages."""

    def save(self, message: ConversationMessage) -> ConversationMessage:
        """Persist a message and return it with its assigned ID."""

    def get_last_messages(self, limit: int = 15) -> list[ConversationMessage]:
        """Return recent messages in chronological order."""
