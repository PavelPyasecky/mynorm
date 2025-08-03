from urllib.parse import quote

from django.conf import settings


def get_yandex_map_link(latitude: float, longitude: float, zoom=15) -> str:
    base_url = settings.YANDEX_MAP_BASE_URL

    return f"{base_url}?ll={longitude},{latitude}&pt={longitude},{latitude}&z={zoom}"