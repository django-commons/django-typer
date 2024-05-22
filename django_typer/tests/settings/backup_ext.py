from .backup import *

INSTALLED_APPS = [
    "django_typer.tests.apps.examples.extensions.my_app",
    "django_typer.tests.apps.examples.extensions.media2",
    *INSTALLED_APPS,
]
