import pytest
from pydantic import ValidationError

from vita.memory.preferences.models import UserPreferences
from vita.memory.preferences.sqlite import SQLitePreferencesRepository
from vita.tools.preferences import PreferencesTool, UpdatePreferencesArgs


def test_updates_only_the_provided_preference(tmp_path) -> None:
    repository = SQLitePreferencesRepository(tmp_path / "vita.db")
    repository.save(UserPreferences(name="Víctor"))

    tool = PreferencesTool(repository)

    updated = tool.update_preferences(
        default_event_duration_minutes=45,
    )

    assert updated == UserPreferences(
        name="Víctor",
        default_event_duration_minutes=45,
    )
    assert repository.load() == updated

def test_rejects_empty_preference_update() -> None:
    with pytest.raises(ValidationError):
        UpdatePreferencesArgs()
def test_rejects_unknown_timezone() -> None:
    with pytest.raises(ValidationError):
        UpdatePreferencesArgs(timezone="Madrid")

def test_rejects_invalid_event_duration() -> None:
    with pytest.raises(ValidationError):
        UpdatePreferencesArgs(default_event_duration_minutes=0)