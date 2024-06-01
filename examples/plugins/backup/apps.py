from django.apps import AppConfig


class BackupConfig(AppConfig):
    name = "django_typer.tests.apps.examples.plugins.backup"
    label = name.replace(".", "_")
