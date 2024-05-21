from django.apps import AppConfig
from django_typer.utils import register_command_extensions


class Extend2Config(AppConfig):
    name = "django_typer.tests.apps.backup.extend2"
    label = name.replace(".", "_")

    def ready(self):
        from .management import extensions
        register_command_extensions(extensions)
