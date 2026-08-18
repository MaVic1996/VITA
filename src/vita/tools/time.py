from datetime import datetime


def get_current_time() -> str:
    """Get the current local date and time."""

    return datetime.now().astimezone().isoformat()