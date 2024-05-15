from .base import *
from pathlib import Path

INSTALLED_APPS = [
    "django_typer.tests.apps.backup.backup",
    "django_typer",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

from django_typer.tests.apps import backup

MEDIA_ROOT = str(Path(backup.__file__).parent / "media")
