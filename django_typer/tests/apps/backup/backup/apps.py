from django.apps import AppConfig


class BackupConfig(AppConfig):
    name = "django_typer.tests.apps.backup.backup"
    label = name.replace(".", "_")
