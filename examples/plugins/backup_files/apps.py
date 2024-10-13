from django.apps import AppConfig

from django_typer.utils import register_command_plugins


class BackupFilesConfig(AppConfig):
    name = "tests.apps.examples.plugins.backup_files"
    label = name.replace(".", "_")
