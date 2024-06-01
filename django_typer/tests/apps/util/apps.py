from django.apps import AppConfig


class UtilConfig(AppConfig):
    name = "django_typer.tests.apps.util"
    label = name.replace(".", "_")
