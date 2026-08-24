import sqlite3
from pathlib import Path

from vita.memory.models import UserPreferences


class SQLitePreferencesRepository:
    DEFAULT_DB_PATH = "data/vita.db"

    def __init__(self, db_path: str = DEFAULT_DB_PATH) -> None:
        self.db_path = db_path
        Path(self.db_path).parent.mkdir(parents=True, exist_ok=True)
        
        self._initialize_database()


    def load(self) -> UserPreferences:
        with sqlite3.connect(self.db_path) as connection:
            row = connection.execute(
                """
                SELECT name, timezone, default_event_duration_minutes, language
                FROM user_preferences
                WHERE id = 1
                """
            ).fetchone()

        if row is None:
            return UserPreferences()

        return UserPreferences(
            name=row[0],
            timezone=row[1],
            default_event_duration_minutes=row[2],
            language=row[3],
        )
    def save(self, preferences: UserPreferences) -> None:
       with sqlite3.connect(self.db_path) as connection:
        connection.execute(
            """
            INSERT INTO user_preferences (
                id,
                name,
                timezone,
                default_event_duration_minutes,
                language
            )
            VALUES (1, ?, ?, ?, ?)
            ON CONFLICT(id) DO UPDATE SET
                name = excluded.name,
                timezone = excluded.timezone,
                default_event_duration_minutes = excluded.default_event_duration_minutes,
                language = excluded.language
            """,
            (
                preferences.name,
                preferences.timezone,
                preferences.default_event_duration_minutes,
                preferences.language,
            ),
        )
        

    def _initialize_database(self) -> None:
        """Initialize the SQLite database and create the preferences table if it doesn't exist."""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            cursor.execute(
                """
                CREATE TABLE IF NOT EXISTS user_preferences (
                    id INTEGER PRIMARY KEY CHECK (id = 1),
                    name TEXT,
                    timezone TEXT NOT NULL,
                    default_event_duration_minutes INTEGER NOT NULL,
                    language TEXT NOT NULL
                )
                """
            )
            conn.commit()