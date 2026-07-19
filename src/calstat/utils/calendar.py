from typing import Any


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
