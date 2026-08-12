from enum import StrEnum


class ConnectorTypes(StrEnum):
    # Mail
    GMAIL = "gmail"
    OUTLOOK_MAIL = "outlook_mail"
    APPLE_MAIL = "apple_mail"

    # Calendar
    GOOGLE_CALENDAR = "google_calendar"
    OUTLOOK_CALENDAR = "outlook_calendar"
    APPLE_CALENDAR = "apple_calendar"

    # Tasks / Notes
    NOTION = "notion"
    TODOIST = "todoist"
    GOOGLE_TASKS = "google_tasks"
    APPLE_REMINDERS = "apple_reminders"

    # Messaging
    SLACK = "slack"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"

    # Project Management
    ASANA = "asana"
    CLICKUP = "clickup"
    JIRA = "jira"
    LINEAR = "linear"

    # Fitness / Health
    STRAVA = "strava"
    GARMIN = "garmin"
    GOOGLE_FIT = "google_fit"
    APPLE_HEALTH = "apple_health"
    FITBIT = "fitbit"
