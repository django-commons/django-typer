from django.apps import AppConfig


class BackupConfig(AppConfig):
    name = "django_typer.tests.apps.examples.extensions.backup"
    label = name.replace(".", "_")
