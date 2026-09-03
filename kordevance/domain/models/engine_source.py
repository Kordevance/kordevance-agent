from enum import StrEnum


class EngineSource(StrEnum):
    """Provenance for a Task/Event: did the goal-cycle agent produce this, or was it created
    directly by the user?
    """

    AGENT = "agent"
    MANUAL = "manual"
