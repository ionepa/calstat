import datetime
from typing import Any


def get_events_between(
    service: Any,
    calendar_id: str,
    time_min: datetime.datetime,
    time_max: datetime.datetime,
    limit: int = 100,
) -> list[dict[str, Any]]:
    """Get events for a calendar between time_min and time_max within the amount limit."""
    if time_min.tzinfo is None or time_max.tzinfo is None:
        raise ValueError("time_min and time_max must include timezone information.")
    if time_min >= time_max:
        raise ValueError("time_min must be earlier than time_max.")

    response = (
        service.events()
        .list(
            calendarId=calendar_id,
            timeMin=time_min.isoformat(),
            timeMax=time_max.isoformat(),
            maxResults=limit,
            singleEvents=True,
            eventTypes=["default"],
            orderBy="startTime",
        )
        .execute()
    )

    # TODO: Check if nextPageToken is non-empty, and if so, ask the user if more events should be shown

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
