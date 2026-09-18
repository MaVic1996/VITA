import sqlite3
from datetime import datetime
from pathlib import Path

from vita.memory.conversation.models import ConversationMessage


class SQLiteConversationRepository:
    DEFAULT_DB_PATH = "data/vita.db"

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)

        self._initialize_database()

    def save(self, message: ConversationMessage) -> ConversationMessage:
        with sqlite3.connect(self.db_path) as connection:
            cursor = connection.execute(
                """
                INSERT INTO conversation_messages (role, content, created_at)
                VALUES (?, ?, ?)
                """,
                (message.role, message.content, message.created_at.isoformat()),
            )

        return ConversationMessage(
            id=cursor.lastrowid,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )

    def get_last_messages(self, limit: int = 15) -> list[ConversationMessage]:
        with sqlite3.connect(self.db_path) as connection:
            rows = connection.execute(
                """
                SELECT id, role, content, created_at
                FROM conversation_messages
                ORDER BY created_at DESC
                LIMIT ?
                """,
                (limit,),
            ).fetchall()

        rows.reverse()
        return [
            ConversationMessage(
                id=row[0],
                role=row[1],
                content=row[2],
                created_at=datetime.fromisoformat(row[3]),
            )
            for row in rows
        ]

    def _initialize_database(self) -> None:
        with sqlite3.connect(self.db_path) as connection:
            connection.execute(
                """
                CREATE TABLE IF NOT EXISTS conversation_messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL CHECK (role IN ('user', 'assistant')),
                    content TEXT NOT NULL,
                    created_at TEXT NOT NULL
                )
                """
            )
