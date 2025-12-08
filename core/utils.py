from datetime import time, datetime, timedelta
from typing import Union, Optional, Any

from django.conf import settings
from django.utils import timezone
from rest_framework import status
from rest_framework.response import Response


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


def success_response(data: Optional[Any] = None, status_code: int = status.HTTP_200_OK) -> Response:
    """
    Args:
        data: Optional response data. If None or empty, will use {"details": "Success."}
        status_code: HTTP status code (default: 200)
    
    Returns:
        Response: DRF Response object with appropriate data and status code
    
    Example:
        >>> success_response()  # Returns {"details": "Success."}
        >>> success_response({"id": 1})  # Returns {"id": 1}
    """
    if data is None or (isinstance(data, dict) and not data):
        data = {"details": "Success."}
    
    return Response(data=data, status=status_code)