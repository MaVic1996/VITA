
from dataclasses import replace
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from vita.memory.models import UserPreferences
from vita.memory.repository import PreferencesRepository


class UpdatePreferencesArgs(BaseModel):
    model_config = ConfigDict(extra="forbid")

    name: str | None = Field(default=None, description="The user's preferred name.")
    timezone: str | None = Field(
        default=None,
        description="The user's preferred timezone, e.g. Europe/Madrid.",
    )
    default_event_duration_minutes: int | None = Field(
        default=None,
        ge=1,
        le=480,
        description="Default calendar event duration in minutes.",
    )
    language: str | None = Field(
        default=None,
        description="The user's preferred language, e.g. es.",
    )

    @field_validator("timezone")
    @classmethod
    def validate_timezone(cls, value: str | None) -> str | None:
        if value is None:
            return None

        try:
            ZoneInfo(value)
        except ZoneInfoNotFoundError as error:
            raise ValueError(f"Unknown timezone: {value}") from error

        return value

    @model_validator(mode="after")
    def require_an_update(self) -> "UpdatePreferencesArgs":
        if not self.model_dump(exclude_none=True):
            raise ValueError("At least one preference must be provided.")

        return self


class PreferencesTool:
    def __init__(self, preferences_repository: PreferencesRepository) -> None:
        self.preferences_repository = preferences_repository

    def update_preferences(
        self,
        name: str | None = None,
        timezone: str | None = None,
        default_event_duration_minutes: int | None = None,
        language: str | None = None,
    ) -> UserPreferences:
        current = self.preferences_repository.load()

        changes = {
            key: value
            for key, value in {
                "name": name,
                "timezone": timezone,
                "default_event_duration_minutes": default_event_duration_minutes,
                "language": language,
            }.items()
            if value is not None
        }

        updated = replace(current, **changes)
        self.preferences_repository.save(updated)

        return updated