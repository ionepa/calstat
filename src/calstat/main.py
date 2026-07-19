import datetime
from typing import cast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

from calstat.utils.calendar import get_all_calendars, get_calendar_labels, select_calendars_by_name
from calstat.utils.config import load_config
from calstat.utils.event import calculate_time_spent, get_events_between
from calstat.utils.file_definitions import CREDENTIALS_FILE, TOKEN_FILE

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]


def authenticate() -> Credentials:
    """Checks if credentials exist, and prompts user to login if they don't."""
    creds = None

    if TOKEN_FILE.exists():
        creds = Credentials.from_authorized_user_file(str(TOKEN_FILE), SCOPES)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(str(CREDENTIALS_FILE), SCOPES)
            creds = cast(Credentials, flow.run_local_server(port=0))

        TOKEN_FILE.write_text(creds.to_json(), encoding="utf-8")

    return creds


def format_duration(duration: datetime.timedelta) -> str:
    """Format a duration as hours and minutes."""
    total_minutes = int(duration.total_seconds() // 60)

    days, remaining_minutes = divmod(total_minutes, 24 * 60)
    hours, minutes = divmod(remaining_minutes, 60)

    parts = []
    if days:
        parts.append(f"{days}d")
    if hours:
        parts.append(f"{hours}h")
    if minutes or not parts:
        parts.append(f"{minutes}m")

    return " ".join(parts)


def main() -> None:
    try:
        creds = authenticate()
        service = build("calendar", "v3", credentials=creds)

        calendars = get_all_calendars(service)
        requested_names, time_min, time_max = load_config()
        selected_calendars = select_calendars_by_name(calendars, requested_names)

        for calendar in selected_calendars:
            calendar_id = calendar["id"]
            calendar_name = calendar.get("summary", calendar_id)
            labels_by_id = get_calendar_labels(service, calendar_id)

            print(f"\n=== {calendar_name} ===")

            events = get_events_between(service, calendar_id, time_min, time_max, limit=100)

            if not events:
                print("No upcoming events.")
                continue

            for event in events:
                title = event.get("summary", "(No title)")
                duration = calculate_time_spent(event)
                label_id = event.get("eventLabelId")

                if isinstance(label_id, str):
                    label_name = labels_by_id.get(label_id, f"(Unknown label: {label_id})")
                else:
                    label_name = "(No label)"

                print()
                print(f"Name:       {title}")
                print(f"Time spent: {format_duration(duration)}")
                print(f"Calendar:   {calendar_name}")
                print(f"Label:      {label_name}")

    except HttpError as error:
        print(f"Google Calendar API error: {error}")
