from zoneinfo import ZoneInfo

from vita.calendar.google import GoogleCalendarClient


def test_formats_naive_datetime_in_the_user_timezone() -> None:
    result = GoogleCalendarClient._format_datetime(
        "2026-09-10T10:00:00",
        ZoneInfo("America/New_York"),
    )

    assert result == {"dateTime": "2026-09-10T10:00:00-04:00"}


def test_formats_all_day_events_without_a_timezone() -> None:
    result = GoogleCalendarClient._format_datetime(
        "2026-09-10",
        ZoneInfo("America/New_York"),
    )

    assert result == {"date": "2026-09-10"}
