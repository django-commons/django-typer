from .backup import *

INSTALLED_APPS = [
    "django_typer.tests.apps.examples.extensions.media1",
    *INSTALLED_APPS,
]
