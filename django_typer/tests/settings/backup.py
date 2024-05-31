from .base import *
from pathlib import Path

INSTALLED_APPS = [
    "django_typer.tests.apps.examples.plugins.backup",
    "django_typer.tests.apps.util",
    "django_typer",
    "django.contrib.admin",
    "django.contrib.auth",
    "django.contrib.contenttypes",
    "django.contrib.sessions",
    "django.contrib.messages",
    "django.contrib.staticfiles",
]

from django_typer.tests.apps import examples

MEDIA_ROOT = str(Path(examples.__file__).parent.parent.parent / "media")
