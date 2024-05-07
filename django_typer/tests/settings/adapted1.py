from .base import *

INSTALLED_APPS = [
    "django_typer.tests.apps.adapter1",
    "django_typer.tests.apps.test_app2",
    *INSTALLED_APPS,
]
