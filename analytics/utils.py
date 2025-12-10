from datetime import date
from typing import Optional
from urllib.parse import quote

from django.conf import settings


def get_yandex_map_link(latitude: float, longitude: float, zoom=15) -> str:
    base_url = settings.YANDEX_MAP_BASE_URL

    return f"{base_url}?ll={longitude},{latitude}&pt={longitude},{latitude}&z={zoom}"


def parse_date_query_param(value: str) -> Optional[date]:
    """Parse a date string from query parameters to a date object."""
    if not value:
        return None
    
    try:
        return date.fromisoformat(value)
    except (ValueError, AttributeError):
        return None


def dates_are_same_day(date1: date, date2: date) -> bool:
    """Check if two dates represent the same day."""
    return date1 == date2