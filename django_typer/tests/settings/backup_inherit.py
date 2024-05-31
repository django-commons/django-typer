from .backup import *

INSTALLED_APPS = [
    "django_typer.tests.apps.examples.plugins.media1",
    *INSTALLED_APPS,
]
