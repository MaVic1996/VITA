from typing import Any, Protocol


class ChatClient(Protocol):
    """Client capable of producing chat responses and tool calls."""

    def chat(
        self,
        messages: list[dict[str, Any]],
        tools: list[dict[str, Any]] | None = None,
    ) -> dict[str, Any]:
        """Return the next assistant message."""
