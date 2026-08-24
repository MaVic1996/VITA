from datetime import datetime

from pydantic import BaseModel


class GetCurrentTimeArgs(BaseModel):
    pass

def get_current_time() -> str:
    """Get the current local date and time."""

    return datetime.now().astimezone().isoformat()