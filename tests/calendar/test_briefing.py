from datetime import datetime
from zoneinfo import ZoneInfo

from vita.calendar.briefing import DailyBriefingService
from vita.memory.preferences.models import UserPreferences


class FakeCalendarClient:
    def __init__(self, events: list[dict]) -> None:
        self.events = events
        self.calls: list[dict] = []

    def list_events(self, **kwargs) -> list[dict]:
        self.calls.append(kwargs)
        return self.events


class FakePreferencesRepository:
    def __init__(self, preferences: UserPreferences) -> None:
        self.preferences = preferences

    def load(self) -> UserPreferences:
        return self.preferences


def build_service(events: list[dict]) -> tuple[DailyBriefingService, FakeCalendarClient]:
    calendar = FakeCalendarClient(events)
    preferences = FakePreferencesRepository(
        UserPreferences(name="Víctor", timezone="Europe/Madrid")
    )
    return DailyBriefingService(calendar, preferences), calendar


def test_reports_when_there_are_no_events() -> None:
    service, calendar = build_service([])
    now = datetime(2026, 9, 12, 8, 0, tzinfo=ZoneInfo("Europe/Madrid"))

    assert service.build(now) == "Hola , Víctor. Hoy no tienes eventos."
    assert calendar.calls == [
        {
            "start": "2026-09-12T00:00:00+02:00",
            "end": "2026-09-13T00:00:00+02:00",
            "timezone": ZoneInfo("Europe/Madrid"),
        }
    ]


def test_lists_events_and_includes_the_next_timed_event() -> None:
    service, _ = build_service(
        [
            {
                "id": "birthday",
                "title": "Cumpleaños de Alba",
                "start": "2026-09-12",
                "end": "2026-09-13",
            },
            {
                "id": "meeting",
                "title": "Reunión con Álvaro",
                "start": "2026-09-12T10:30:00+02:00",
                "end": "2026-09-12T11:30:00+02:00",
            },
        ]
    )
    now = datetime(2026, 9, 12, 9, 0, tzinfo=ZoneInfo("Europe/Madrid"))

    assert service.build(now) == (
        "Hola , Víctor. Hoy tienes 2 eventos:\n"
        "- Todo el día: Cumpleaños de Alba\n"
        "- 10:30: Reunión con Álvaro\n"
        "Tu próximo evento es Reunión con Álvaro a las 10:30, "
        "empieza dentro de 1 hora y 30 minutos."
    )
