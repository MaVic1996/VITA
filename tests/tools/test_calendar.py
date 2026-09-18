from zoneinfo import ZoneInfo

from vita.memory.preferences.models import UserPreferences
from vita.tools.calendar import CalendarTool


class FakeCalendarClient:
    def __init__(self) -> None:
        self.calls: list[dict] = []

    def list_events(self, **kwargs) -> list[dict]:
        self.calls.append(kwargs)
        return []


class FakePreferencesRepository:
    def load(self) -> UserPreferences:
        return UserPreferences(timezone="America/New_York")


def test_uses_the_saved_timezone_when_listing_events() -> None:
    calendar = FakeCalendarClient()
    tool = CalendarTool(calendar, FakePreferencesRepository())

    assert tool.list_events("2026-09-10T00:00:00", "2026-09-10T23:59:59") == []

    assert calendar.calls == [
        {
            "start": "2026-09-10T00:00:00",
            "end": "2026-09-10T23:59:59",
            "timezone": ZoneInfo("America/New_York"),
        }
    ]
