
from datetime import datetime, timedelta
from typing import Any
from zoneinfo import ZoneInfo

from vita.calendar.google import GoogleCalendarClient
from vita.memory.repository import PreferencesRepository


class DailyBriefingService:
    def __init__(self, 
                 calendar_client: GoogleCalendarClient,
                 preferences_repository: PreferencesRepository):
        self.calendar_client = calendar_client
        self.preferences_repository = preferences_repository

    def build(self, now: datetime | None = None):
        preferences = self.preferences_repository.load()
        timezone = ZoneInfo(preferences.timezone)
        current_time = self._localize(now, timezone)

        day_start = datetime.combine(current_time.date(), datetime.min.time(), tzinfo=timezone)
        next_day_start = day_start + timedelta(days=1)

        events = self.calendar_client.list_events(start=day_start.isoformat(), end=next_day_start.isoformat(), timezone=timezone)

        name = f", {preferences.name}" if preferences.name else ""

        if not events:
            return f"Hola {name}. Hoy no tienes eventos."

        sorted_events = sorted(events, key=lambda event: event['start'])
        event_lines = "\n".join(
            f"- {self._event_description(event)}"
            for event in sorted_events
        )

        event_count = len(sorted_events)
        event_label = "evento" if event_count == 1 else "eventos"

        briefing = f"Hola {name}. Hoy tienes {event_count} {event_label}:\n{event_lines}"

        next_event = self._next_event(sorted_events, current_time, timezone)
        if next_event:
            event_time = self._event_datetime(next_event, timezone)
            briefing += (
                f"\nTu próximo evento es {next_event['title']} a las "
                f"{event_time:%H:%M}, {self._time_until(event_time - current_time)}."
            )
        return briefing

    def _next_event(self, sorted_events: list[dict[str, Any]], current_time: datetime, timezone: ZoneInfo):
        for event in sorted_events:
            if "T" not in event['start']:
                continue

            if self._event_datetime(event, timezone) >= current_time:
                return event
        return None

    @staticmethod
    def _localize(date_time: datetime | None, timezone: ZoneInfo) -> datetime:
        if date_time is None:
            date_time = datetime.now(timezone)

        return date_time.astimezone(timezone)

    @staticmethod
    def _event_description(event: dict[str, Any]):
        if "T" not in event['start']:
            return f"Todo el día: {event['title']}"

        event_time = datetime.fromisoformat(event['start'])
        return f"{event_time.strftime('%H:%M')}: {event['title']}"

    @staticmethod
    def _event_datetime(event: dict[str, Any], timezone: ZoneInfo) -> datetime:
        event_time = datetime.fromisoformat(event['start'])

        if event_time.tzinfo is None:
            event_time = event_time.replace(tzinfo=timezone)

        return event_time.astimezone(timezone)

    @staticmethod
    def _time_until(delta: timedelta) -> str:
        total_minutes = max(0,  int(delta.total_seconds() // 60))

        if total_minutes  == 0:
            return "empieza ahora"

        hours, minutes = divmod(total_minutes, 60)
        if hours == 0:
            return f"empieza dentro de {minutes} {'minuto' if minutes == 1 else 'minutos'}"

        if minutes == 0:
            unit = "hora" if hours == 1 else "horas"
            return f"empieza dentro de {hours} {unit}"

        hour_unit = "hora" if hours == 1 else "horas"
        minute_unit = "minuto" if minutes == 1 else "minutos"
        return f"empieza dentro de {hours} {hour_unit} y {minutes} {minute_unit}"

    