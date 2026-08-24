from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class PendingToolCall:
    tool_name: str
    arguments: dict[str, Any]
    confirmation_message: str