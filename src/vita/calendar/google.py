from pathlib import Path
from datetime import datetime
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


    def list_events(self, start_date: datetime, end_date: datetime) -> list[dict[str, Any]]:
        service = self._get_service()

        result = (
            service.events()
            .list(
                calendarId="primary",
                timeMin=start_date.isoformat(),
                timeMax=end_date.isoformat(),
                singleEvents=True,
                orderBy="startTime",
            )
            .execute()
        )

        return [self._normalize_event(event) for event in result.get("items", [])]

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

    def _normalize_event(self, event: dict) -> dict:
        start_date = event.get("start", {})
        end_date = event.get("end", {})

        return {
            "id": event.get("id"),
            "title": event.get("summary", "Sin título"),
            "start": start_date.get("dateTime", start_date.get("date")),
            "end": end_date.get("dateTime", end_date.get("date")),
        }