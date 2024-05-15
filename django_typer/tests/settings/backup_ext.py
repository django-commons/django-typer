from .backup import *

INSTALLED_APPS = [
    "django_typer.tests.apps.backup.extend2",
    "django_typer.tests.apps.backup.extend1",
    *INSTALLED_APPS,
]
