from .settings import *

INSTALLED_APPS = [
    "django_typer.tests.adapter1",
    "django_typer.tests.adapter2",
    *INSTALLED_APPS
]
