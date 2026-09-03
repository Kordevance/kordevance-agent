from datetime import UTC, datetime
from zoneinfo import ZoneInfo

from kordevance.domain.models.goal import Goal
from kordevance.domain.models.profile import Profile
from kordevance.domain.models.tz import TimezoneMode


def as_aware_utc(value: datetime) -> datetime:
    return value if value.tzinfo is not None else value.replace(tzinfo=UTC)


def resolve_execution_timezone(goal: Goal, profile: Profile) -> ZoneInfo:
    if goal.timezone_mode == TimezoneMode.FIXED and goal.specific_timezone:
        tz_str = goal.specific_timezone
    elif goal.timezone_mode == TimezoneMode.HOME:
        tz_str = profile.home_timezone
    else:
        tz_str = profile.last_known_timezone

    try:
        return ZoneInfo(tz_str)
    except Exception:
        return ZoneInfo("UTC")
