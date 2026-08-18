from pathlib import Path
from datetime import datetime, timezone
from typing import Any

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import Resource, build


class GoogleCalendarClient:
    SCOPES = ["https://www.googleapis.com/auth/calendar"]

    def __init__(
        self,
        credentials_path: str = "credentials/google_client_secret.json",
        token_path: str = "credentials/token.json",
    ) -> None:
        self.credentials_path = Path(credentials_path)
        self.token_path = Path(token_path)
        self._service: Resource | None = None


    def list_events(self, start: str, end: str) -> list[dict[str, Any]]:
        service = self._get_service()

        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=self._ensure_rfc3339(start),
                timeMax=self._ensure_rfc3339(end),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return [self._normalize_event(event) for event in result.get("items", [])]

    def create_event(
        self,
        title: str,
        start: str,
        end: str,
        description: str | None = None,
        location: str | None = None,
    ) -> dict:
        service = self._get_service()

        event = {
            "summary": title,
            "start": self._format_datetime(start),
            "end": self._format_datetime(end),
        }

        if description:
            event["description"] = description

        if location:
            event["location"] = location

        created_event = service.events().insert(calendarId="primary", body=event).execute()
        return self._normalize_event(created_event)


    def update_event(
        self,
        event_id: str,
        title: str | None = None,
        start: str | None = None,
        end: str | None = None,
        description: str | None = None,
        location: str | None = None,
    ) -> dict:
        service = self._get_service()

        event = service.events().get(calendarId="primary", eventId=event_id).execute()

        if title:
            event["summary"] = title
        if start:
            event["start"]= self._format_datetime(start)
        if end:
            event["end"] = self._format_datetime(end)
        if description:
            event["description"] = description
        if location:
            event["location"] = location

        updated_event = service.events().patch(calendarId="primary", eventId=event_id, body=event).execute()
        return self._normalize_event(updated_event)

    def delete_event(self, event_id: str) -> None:
        service = self._get_service()
        service.events().delete(calendarId="primary", eventId=event_id).execute()

    @staticmethod
    def _ensure_rfc3339(dt: str) -> str:
        parsed = datetime.fromisoformat(dt)
        if parsed.tzinfo is None:
            parsed = parsed.replace(tzinfo=timezone.utc)
        return parsed.isoformat()

    @staticmethod
    def _format_datetime(dt: str) -> dict:
        if "T" not in dt:
            return { "date": dt }

        return { "dateTime": dt }

    @staticmethod
    def _normalize_event(event: dict) -> dict:
        start_date = event.get("start", {})
        end_date = event.get("end", {})

        return {
            "id": event.get("id"),
            "title": event.get("summary", "Sin título"),
            "start": start_date.get("dateTime", start_date.get("date")),
            "end": end_date.get("dateTime", end_date.get("date")),
        }
    
    def _authenticate(self) -> Credentials:
        credentials = None

        if self.token_path.exists():
            credentials = Credentials.from_authorized_user_file(
                self.token_path,
                self.SCOPES,
            )

        if not credentials or not credentials.valid:
            if credentials and credentials.expired and credentials.refresh_token:
                credentials.refresh(Request())
            else:
                flow = InstalledAppFlow.from_client_secrets_file(
                    self.credentials_path,
                    self.SCOPES,
                )
                credentials = flow.run_local_server(port=0)

            self.token_path.write_text(credentials.to_json())

        return credentials

    def _get_service(self) -> Resource:
        if self._service is None:
            credentials = self._authenticate()

            self._service = build(
                "calendar",
                "v3",
                credentials=credentials,
            )

        return self._service