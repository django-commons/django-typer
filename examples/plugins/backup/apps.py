from django.apps import AppConfig


class BackupConfig(AppConfig):
    name = "tests.apps.examples.plugins.backup"
    label = name.replace(".", "_")
