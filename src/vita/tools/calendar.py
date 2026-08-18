from datetime import datetime

from vita.calendar.google import GoogleCalendarClient


class CalendarTool:
    def __init__(self, calendar: GoogleCalendarClient) -> None:
        self.calendar = calendar

    def list_events(
        self,
        start: str,
        end: str,
    ) -> list[dict]:
        start_datetime = datetime.fromisoformat(start)
        end_datetime = datetime.fromisoformat(end)

        return self.calendar.list_events(
            start_date=start_datetime,
            end_date=end_datetime,
        )