from datetime import datetime
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

_UNKNOWN_TIMEZONE_NOTE = "the user's timezone is not known. Say so plainly if needed."


def describe_current_datetime(now: datetime, timezone: str | None) -> str:
    if not timezone:
        return f"{now.isoformat()} UTC ({_UNKNOWN_TIMEZONE_NOTE})"

    try:
        local = now.astimezone(ZoneInfo(timezone))
    except ZoneInfoNotFoundError:
        return f"{now.isoformat()} UTC ({_UNKNOWN_TIMEZONE_NOTE})"

    return f"{now.isoformat()} UTC ({local.isoformat()} in the user's timezone, {timezone})"
