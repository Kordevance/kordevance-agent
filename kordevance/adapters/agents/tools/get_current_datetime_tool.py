from datetime import UTC, datetime


def get_current_datetime() -> str:
    """Get the current date and time in UTC.

    Use this tool whenever you need to know the current date, time, day of
    the week, or perform any calculation that depends on "now" (e.g.,
    determining relative dates like "tomorrow" or "next Monday", checking
    if a deadline has passed, or computing durations up to the present).

    Returns:
        str: The current UTC datetime in ISO 8601 format
    """
    return datetime.now(UTC).isoformat()
