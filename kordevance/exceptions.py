class BadRequestError(Exception):
    pass


class ItemNotFoundError(Exception):
    pass


class ConnectionMissingError(Exception):
    """Raised when a tool execution is attempted but the device has no valid connection for
    that tool's provider/category. (Re)authorize it via connections/session, then retry."""

    pass
