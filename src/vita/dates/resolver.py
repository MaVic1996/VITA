from __future__ import annotations

import re
import unicodedata
from dataclasses import dataclass
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo

WEEKDAYS = {
    "lunes": 0,
    "martes": 1,
    "miercoles": 2,
    "jueves": 3,
    "viernes": 4,
    "sabado": 5,
    "domingo": 6,
}

NUMBER_WORDS = {
    "un": 1,
    "una": 1,
    "dos": 2,
    "tres": 3,
    "cuatro": 4,
    "cinco": 5,
    "seis": 6,
    "siete": 7,
    "ocho": 8,
    "nueve": 9,
    "diez": 10,
}


@dataclass(frozen=True)
class DateResolution:
    expression: str
    value: str


class RelativeDateResolver:
    """Resolve common Spanish calendar expressions without relying on the LLM."""

    def __init__(self, timezone_name: str = "Europe/Madrid") -> None:
        self.timezone = ZoneInfo(timezone_name)

    def resolve(
        self, text: str, now: datetime | None = None
    ) -> list[DateResolution]:
        current = self._localize_now(now)
        normalized = self._normalize(text)
        resolutions: list[DateResolution] = []

        if "pasado manana" in normalized:
            resolutions.append(
                DateResolution("pasado mañana", self._date_value(current, 2))
            )
        elif "manana" in normalized:
            resolutions.append(DateResolution("mañana", self._date_value(current, 1)))
        elif re.search(r"\bhoy\b", normalized):
            resolutions.append(DateResolution("hoy", self._date_value(current, 0)))

        resolutions.extend(self._resolve_in_duration(normalized, current))
        resolutions.extend(self._resolve_weekdays(normalized, current))
        resolutions.extend(self._resolve_ranges(normalized, current))
        return resolutions

    def context_for(self, text: str, now: datetime | None = None) -> str | None:
        resolutions = self.resolve(text, now)
        if not resolutions:
            return None

        details = "\n".join(
            f'- "{resolution.expression}" = {resolution.value}'
            for resolution in resolutions
        )
        return (
            "Calendar date references have been resolved deterministically in "
            f"{self.timezone.key}:\n{details}\n"
            "Use these exact values when calling calendar tools; do not recalculate them."
        )

    def _resolve_in_duration(
        self, text: str, now: datetime
    ) -> list[DateResolution]:
        match = re.search(
            r"\bdentro de (un|una|dos|tres|cuatro|cinco|seis|siete|ocho|"
            r"nueve|diez|\d+) (minutos?|horas?|dias?|semanas?)\b",
            text,
        )
        if not match:
            return []

        quantity_text, unit = match.groups()
        quantity = NUMBER_WORDS.get(quantity_text, int(quantity_text) if quantity_text.isdigit() else 0)
        if unit.startswith("minuto"):
            delta = timedelta(minutes=quantity)
        elif unit.startswith("hora"):
            delta = timedelta(hours=quantity)
        elif unit.startswith("dia"):
            delta = timedelta(days=quantity)
        else:
            delta = timedelta(weeks=quantity)

        return [DateResolution(match.group(0), (now + delta).isoformat(timespec="seconds"))]

    def _resolve_weekdays(self, text: str, now: datetime) -> list[DateResolution]:
        results: list[DateResolution] = []
        for name, weekday in WEEKDAYS.items():
            match = re.search(rf"\b(?:(este|proximo) )?{name}\b", text)
            if not match:
                continue

            days = (weekday - now.weekday()) % 7
            if days == 0:
                days += 7

            results.append(DateResolution(match.group(0), self._date_value(now, days)))
        return results

    def _resolve_ranges(self, text: str, now: datetime) -> list[DateResolution]:
        next_monday = now.date() + timedelta(days=(7 - now.weekday()))
        if "la semana que viene" in text:
            return [
                DateResolution(
                    "la semana que viene",
                    f"{next_monday.isoformat()} to {(next_monday + timedelta(days=6)).isoformat()}",
                )
            ]

        if "este fin de semana" in text:
            saturday = now.date() + timedelta(days=(5 - now.weekday()) % 7)
            return [
                DateResolution(
                    "este fin de semana",
                    f"{saturday.isoformat()} to {(saturday + timedelta(days=1)).isoformat()}",
                )
            ]
        return []

    def _localize_now(self, now: datetime | None) -> datetime:
        current = now or datetime.now(self.timezone)
        if current.tzinfo is None:
            return current.replace(tzinfo=self.timezone)
        return current.astimezone(self.timezone)

    @staticmethod
    def _normalize(text: str) -> str:
        return "".join(
            char
            for char in unicodedata.normalize("NFD", text.lower())
            if unicodedata.category(char) != "Mn"
        )

    @staticmethod
    def _date_value(now: datetime, days: int) -> str:
        return (now + timedelta(days=days)).date().isoformat()
