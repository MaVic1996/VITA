from dataclasses import dataclass


@dataclass(frozen=True)
class UserPreferences:
    """User preferences for the VITA agent."""
    name: str | None = None
    timezone: str = "Europe/Madrid"
    default_event_duration_minutes: int = 60
    language: str = "es"  # Default language is Spanish