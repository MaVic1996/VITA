from datetime import datetime
from zoneinfo import ZoneInfo

from vita.dates.resolver import RelativeDateResolver

MADRID = ZoneInfo("Europe/Madrid")
NOW = datetime(2026, 8, 19, 14, 30, tzinfo=MADRID)  # Wednesday


def test_resolves_today_tomorrow_and_day_after_tomorrow() -> None:
    resolver = RelativeDateResolver()

    assert resolver.resolve("¿Qué tengo hoy?", NOW)[0].value == "2026-08-19"
    assert resolver.resolve("Mañana a las 10", NOW)[0].value == "2026-08-20"
    assert resolver.resolve("Pasado mañana", NOW)[0].value == "2026-08-21"


def test_resolves_relative_durations_with_local_timezone() -> None:
    resolver = RelativeDateResolver()

    result = resolver.resolve("Recuérdamelo dentro de dos horas", NOW)

    assert result[0].expression == "dentro de dos horas"
    assert result[0].value == "2026-08-19T16:30:00+02:00"


def test_resolves_weekdays_and_ranges() -> None:
    resolver = RelativeDateResolver()

    assert resolver.resolve("El viernes", NOW)[0].value == "2026-08-21"
    assert resolver.resolve("El próximo lunes", NOW)[0].value == "2026-08-24"
    assert resolver.resolve("La semana que viene", NOW)[0].value == "2026-08-24 to 2026-08-30"
