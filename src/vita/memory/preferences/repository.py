from typing import Protocol

from vita.memory.preferences.models import UserPreferences


class PreferencesRepository(Protocol):
    """Protocol for a repository that manages user preferences."""

    def load(self) -> UserPreferences:
        """Retrieve the user preferences."""

    def save(self, preferences: UserPreferences) -> None:
        """Save the user preferences."""
