import datetime
import tomllib

from calstat.utils.file_definitions import FILTERS_FILE


def load_config() -> tuple[list[str], datetime.datetime, datetime.datetime]:
    """Reads calendar names from file, and ensures at least one calendar is present. Reads times and ensures correctness"""
    with FILTERS_FILE.open("rb") as file:
        config = tomllib.load(file)

    names = config.get("calendars")

    if not isinstance(names, list) or not all(isinstance(name, str) for name in names):
        raise ValueError('calendars.toml must contain a string list named "calendars".')
    if not names:
        raise ValueError("No calendars were configured.")

    time_min = parse_config_datetime(config.get("time_min"), "time_min")
    time_max = parse_config_datetime(config.get("time_max"), "time_max")

    if time_min >= time_max:
        raise ValueError('"time_min" must be earlier than "time_max".')

    return names, time_min, time_max


def parse_config_datetime(value: object, field_name: str) -> datetime.datetime:
    if not isinstance(value, str):
        raise ValueError(f'"{field_name}" must be a string.')

    try:
        parsed = datetime.datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as error:
        raise ValueError(
            f'"{field_name}" must be an ISO 8601 timestamp, '
            'for example "2026-07-01T00:00:00+02:00".'
        ) from error

    if parsed.tzinfo is None:
        raise ValueError(f'"{field_name}" must include a timezone offset.')

    return parsed
