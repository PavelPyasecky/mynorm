import logging
import os

import django

os.environ.get("DJANGO_SETTINGS_MODULE", "config.settings.local")
django.setup()

from django.contrib.auth import get_user_model  # noqa: E402

User = get_user_model()

username = os.getenv("DJANGO_SUPERUSER_USERNAME", "admin")
email = os.getenv("DJANGO_SUPERUSER_EMAIL", "admin@example.com")
password = os.getenv("DJANGO_SUPERUSER_PASSWORD", "passNOTword")

logger = logging.Logger(__name__)

if not User.objects.filter(username=username).exists():
    User.objects.create_superuser(username, email, password)
    logger.info("Superuser created successfully!")
else:
    logger.info("Superuser already exists.")
