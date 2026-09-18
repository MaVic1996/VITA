from dataclasses import dataclass
from datetime import datetime
from typing import Literal


@dataclass(frozen=True)
class ConversationMessage:
    role: Literal["user", "assistant"]
    content: str
    created_at: datetime
    id: int | None = None
