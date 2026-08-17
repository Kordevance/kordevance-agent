from enum import StrEnum

from pydantic import BaseModel


class ConnectorProviders(StrEnum):
    GOOGLE = "google"
    MICROSOFT = "microsoft"
    APPLE = "apple"
    NOTION = "notion"
    TODOIST = "todoist"
    SLACK = "slack"
    TELEGRAM = "telegram"
    WHATSAPP = "whatsapp"
    ASANA = "asana"
    CLICKUP = "clickup"
    JIRA = "jira"
    LINEAR = "linear"
    STRAVA = "strava"
    GARMIN = "garmin"
    FITBIT = "fitbit"


class ConnectorTypes(StrEnum):
    MAIL = "mail"
    CALENDAR = "calendar"
    TASKS = "tasks"
    HEALTH = "health"
    NOTES = "notes"
    MESSAGING = "messaging"


class Connector(BaseModel):
    provider: ConnectorProviders
    category: ConnectorTypes
