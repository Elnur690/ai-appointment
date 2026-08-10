from datetime import datetime
from zoneinfo import ZoneInfo

def to_utc(dt: datetime, tz: str) -> datetime:
    """Convert a naive or aware datetime in a specific timezone to UTC."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo(tz))
    return dt.astimezone(ZoneInfo("UTC"))

def from_utc(dt: datetime, tz: str) -> datetime:
    """Convert a UTC datetime to a specific timezone."""
    if dt.tzinfo is None:
        dt = dt.replace(tzinfo=ZoneInfo("UTC"))
    return dt.astimezone(ZoneInfo(tz))

def get_current_time(tz: str) -> datetime:
    """Get the current time in a specific timezone."""
    return datetime.now(ZoneInfo(tz))

def get_day_of_week(dt: datetime, tz: str) -> int:
    """
    Get the day of the week for a datetime in a specific timezone.
    Returns 0=Monday to 6=Sunday.
    """
    local_dt = dt
    if dt.tzinfo is None or str(dt.tzinfo) != tz:
        if dt.tzinfo is None:
            local_dt = dt.replace(tzinfo=ZoneInfo("UTC")).astimezone(ZoneInfo(tz))
        else:
            local_dt = dt.astimezone(ZoneInfo(tz))
    return local_dt.weekday()
