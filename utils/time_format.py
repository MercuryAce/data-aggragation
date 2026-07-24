from datetime import datetime, timezone


def _as_utc(value: datetime) -> datetime:
    if value.tzinfo is None:
        return value.replace(tzinfo=timezone.utc)
    return value.astimezone(timezone.utc)


def human_age(fetched_at: datetime) -> str:
    """Format the age of a cached item in a human-readable way."""
    now = datetime.now(timezone.utc)
    diff = now - _as_utc(fetched_at)
    seconds = int(diff.total_seconds())

    if seconds < 60:
        return f"{seconds} seconds ago"
    if seconds < 3600:
        return f"{seconds // 60} minutes ago"
    if seconds < 86400:
        return f"{seconds // 3600} hours ago"
    return f"{seconds // 86400} days ago"
