from .base import *

INSTALLED_APPS = [
    "django_typer.tests.apps.adapter0",
    "django_typer.tests.apps.test_app2",
    *INSTALLED_APPS,
]
