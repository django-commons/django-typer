from .backup import *

INSTALLED_APPS = [
    "django_typer.tests.apps.examples.plugins.my_app",
    "django_typer.tests.apps.examples.plugins.media2",
    *INSTALLED_APPS,
]
