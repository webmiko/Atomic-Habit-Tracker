"""WSGI: Django API + статика фронтенда из каталога frontend/."""

import os
from pathlib import Path

from django.core.wsgi import get_wsgi_application
from whitenoise import WhiteNoise

BASE_DIR = Path(__file__).resolve().parent.parent
os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")

django_app = get_wsgi_application()
application = WhiteNoise(
    django_app,
    root=str(BASE_DIR / "frontend"),
    prefix="",
    index_file="login.html",
)
