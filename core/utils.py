from datetime import time, datetime, timedelta
from typing import Union

from django.conf import settings
from django.utils import timezone


def timedelta_to_str(td):
    """Convert timedelta to time object (ignoring days)"""
    total_seconds = int(td.total_seconds())
    hours = (total_seconds // 3600) % 24  # Wrap around 24 hours
    minutes = (total_seconds // 60) % 60
    seconds = total_seconds % 60

    microseconds = td.microseconds
    return time(hour=hours, minute=minutes, second=seconds, microsecond=microseconds).strftime("%H:%M:%S")


def localize_datetime(datetime_, tz=settings.ADMIN_TIME_ZONE) -> Union[datetime, None]:
    return datetime_.astimezone(tz)


def time_difference(start_time, end_time):
    today = timezone.now().today()
    start_dt = datetime.combine(today, start_time)
    end_dt = datetime.combine(today, end_time)

    if end_time < start_time:
        end_dt += timedelta(days=1)

    return end_dt - start_dt