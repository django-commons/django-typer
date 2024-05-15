from django.apps import AppConfig


class InheritConfig(AppConfig):
    name = "django_typer.tests.apps.backup.inherit"
    label = name.replace(".", "_")
