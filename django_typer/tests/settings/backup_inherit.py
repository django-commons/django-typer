from .backup import *

INSTALLED_APPS = [
    "django_typer.tests.apps.backup.inherit",
    *INSTALLED_APPS,
]
