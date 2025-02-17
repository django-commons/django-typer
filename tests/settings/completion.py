from .base import *

INSTALLED_APPS = [
    "tests.apps.completion",
    "tests.apps.util",
    "django_typer",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

MEDIA_ROOT = str(BASE_DIR / "media")

STATIC_ROOT = BASE_DIR / "static"
