import datetime
import tomllib
from pathlib import Path
from typing import Any, cast

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ["https://www.googleapis.com/auth/calendar.readonly"]

CREDENTIALS_FILE = Path("data/credentials.json")
TOKEN_FILE = Path("data/token.json")
FILTERS_FILE = Path("data/calendars.toml")


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


def load_requested_calendar_names() -> list[str]:
    """Reads calendar names from file, and ensures at least one calendar is present."""
    with FILTERS_FILE.open("rb") as file:
        config = tomllib.load(file)

    names = config.get("calendars")

    if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
        raise ValueError('calendars.toml must contain a string list named "calendars".')
    if not names:
        raise ValueError("No calendars were configured.")

    return names


def get_all_calendars(service: Any) -> list[dict[str, Any]]:
    """Gets all calendars of a user."""
    calendars = []
    page_token = None

    while True:
        response = service.calendarList().list(pageToken=page_token).execute()

        calendars.extend(response.get("items", []))
        page_token = response.get("nextPageToken")

        if not page_token:
            break

    return calendars


def get_calendar_labels(service: Any, calendar_id: str) -> dict[str, str]:
    """Return a mapping of event label ID to readable label name."""
    calendar = service.calendars().get(calendarId=calendar_id).execute()

    label_properties = calendar.get("labelProperties", {})
    event_labels = label_properties.get("eventLabels", [])

    labels_by_id = {}

    for label in event_labels:
        label_id = label.get("id")
        label_name = label.get("name")

        if isinstance(label_id, str):
            labels_by_id[label_id] = (
                label_name if isinstance(label_name, str) and label_name else "(Unnamed label)"
            )

    return labels_by_id


def select_calendars_by_name(
    available_calendars: list[dict[str, Any]], requested_names: list[str]
) -> list[dict[str, Any]]:
    """Returns all calendars requested, and ensures all calendars requested exist and are unique."""
    calendars_by_name: dict[str, list[dict[str, Any]]] = {}

    for calendar in available_calendars:
        name = calendar.get("summary")

        if isinstance(name, str):
            calendars_by_name.setdefault(name, []).append(calendar)

    missing = [name for name in requested_names if name not in calendars_by_name]

    if missing:
        raise ValueError(
            "The following calendars do not exist or are not accessible: " + ", ".join(missing)
        )

    duplicates = [name for name in requested_names if len(calendars_by_name[name]) > 1]

    if duplicates:
        raise ValueError(
            "Multiple calendars have the following names: "
            + ", ".join(duplicates)
            + ". Configure them by calendar ID instead."
        )

    return [calendars_by_name[name][0] for name in requested_names]


def get_upcoming_events(service: Any, calendar_id: str, limit: int = 100) -> list[dict[str, Any]]:
    """Get upcoming events for a calendar from the current time until the limit."""
    now = datetime.datetime.now(datetime.UTC).isoformat()

    response = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=now,
            maxResults=limit,
            singleEvents=True,
            orderBy="startTime",
        )
        .execute()
    )

    return response.get("items", [])


def parse_event_time(time_data: dict[str, Any]) -> datetime.datetime | datetime.date:
    """Parse an event start or end value."""
    if "dateTime" in time_data:
        return datetime.datetime.fromisoformat(time_data["dateTime"])

    if "date" in time_data:
        return datetime.date.fromisoformat(time_data["date"])

    raise ValueError("Event has no start or end time.")


def calculate_time_spent(event: dict[str, Any]) -> datetime.timedelta:
    """Calculate the duration of a timed or all-day event."""
    start = parse_event_time(event["start"])
    end = parse_event_time(event["end"])

    if isinstance(start, datetime.datetime) and isinstance(end, datetime.datetime):
        return end - start

    if (
        isinstance(start, datetime.date)
        and not isinstance(start, datetime.datetime)
        and isinstance(end, datetime.date)
        and not isinstance(end, datetime.datetime)
    ):
        return end - start

    raise ValueError("Event start and end use different formats.")


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
        requested_names = load_requested_calendar_names()
        selected_calendars = select_calendars_by_name(calendars, requested_names)

        for calendar in selected_calendars:
            calendar_id = calendar["id"]
            calendar_name = calendar.get("summary", calendar_id)
            labels_by_id = get_calendar_labels(service, calendar_id)

            print(f"\n=== {calendar_name} ===")

            events = get_upcoming_events(service, calendar_id, limit=100)

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
