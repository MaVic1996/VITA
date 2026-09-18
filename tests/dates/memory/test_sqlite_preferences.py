from vita.memory.preferences.models import UserPreferences
from vita.memory.preferences.sqlite import SQLitePreferencesRepository


def test_load_returns_default_preferences_when_empty(tmp_path) -> None:
    repository = SQLitePreferencesRepository(tmp_path / "vita.db")

    assert repository.load() == UserPreferences()


def test_save_persists_and_updates_preferences(tmp_path) -> None:
    repository = SQLitePreferencesRepository(tmp_path / "vita.db")

    repository.save(UserPreferences(name="Víctor"))
    repository.save(
        UserPreferences(
            name="Víctor",
            default_event_duration_minutes=45,
        )
    )

    assert repository.load() == UserPreferences(
        name="Víctor",
        default_event_duration_minutes=45,
    )