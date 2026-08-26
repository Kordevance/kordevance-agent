from enum import StrEnum


class TimezoneMode(StrEnum):
    FLOATING = "floating"  # Uses profile.last_known_timezone (moves with user)
    HOME = "home"  # Uses profile.home_timezone (anchored to user home)
    FIXED = "fixed"  # Uses goal.specific_timezone (anchored to location)
