from zoneinfo import ZoneInfo

from pydantic import BaseModel, Field

from vita.calendar.google import GoogleCalendarClient
from vita.memory.preferences.repository import PreferencesRepository


class ListEventsArgs(BaseModel):
    start: str = Field(
        description="Start of the period in ISO 8601 format.",
    )
    end: str = Field(
        description="End of the period in ISO 8601 format.",
    )


class CreateEventArgs(BaseModel):
    title: str = Field(
        description="Title of the event.",
    )
    start: str = Field(
        description="Start of the event in ISO 8601 format.",
    )
    end: str = Field(
        description="End of the event in ISO 8601 format.",
    )
    description: str | None = Field(
        default=None,
        description="Description of the event (optional).",
    )
    location: str | None = Field(
        default=None,
        description="Location of the event (optional).",
    ) 

class UpdateEventArgs(BaseModel):
    event_id: str = Field(
        description="ID of the event to update.",
    )
    title: str | None = Field(
        default=None,
        description="New title of the event (optional).",
    )
    start: str | None = Field(
        default=None,
        description="New start of the event in ISO 8601 format (optional).",
    )
    end: str | None = Field(
        default=None,
        description="New end of the event in ISO 8601 format (optional).",
    )
    description: str | None = Field(
        default=None,
        description="New description of the event (optional).",
    )
    location: str | None = Field(
        default=None,
        description="New location of the event (optional).",
    )

class DeleteEventArgs(BaseModel):
    event_id: str = Field(
        description="ID of the event to delete.",
    )


class CalendarTool:
    def __init__(
        self,
        calendar: GoogleCalendarClient,
        preferences_repository: PreferencesRepository,
    ) -> None:
        self.calendar = calendar
        self.preferences_repository = preferences_repository

    def list_events(
        self,
        start: str,
        end: str,
    ) -> list[dict]:
        return self.calendar.list_events(
            start=start,
            end=end,
            timezone=self._user_timezone(),
        )

    def create_event(
        self,
        title: str,
        start: str,
        end: str,
        description: str | None = None,
        location: str | None = None,
    ) -> dict:

        return self.calendar.create_event(
            title=title,
            start=start,
            end=end,
            description=description,
            location=location,
            timezone=self._user_timezone(),
        )

    def update_event(
        self,
        event_id: str,
        title: str | None = None,
        start: str | None = None,
        end: str | None = None,
        description: str | None = None,
        location: str | None = None,
    ) -> dict:

        return self.calendar.update_event(
            event_id=event_id,
            title=title,
            start=start,
            end=end,
            description=description,
            location=location,
            timezone=self._user_timezone(),
        )

    def delete_event(self, event_id: str) -> str:
        self.calendar.delete_event(event_id)

        return f"Event with ID {event_id} has been deleted."

    def _user_timezone(self) -> ZoneInfo:
        return ZoneInfo(self.preferences_repository.load().timezone)
