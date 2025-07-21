from datetime import time


def timedelta_to_str(td):
    """Convert timedelta to time object (ignoring days)"""
    total_seconds = int(td.total_seconds())
    hours = (total_seconds // 3600) % 24  # Wrap around 24 hours
    minutes = (total_seconds // 60) % 60
    seconds = total_seconds % 60

    microseconds = td.microseconds
    return time(hour=hours, minute=minutes, second=seconds, microsecond=microseconds).strftime("%H:%M:%S")
