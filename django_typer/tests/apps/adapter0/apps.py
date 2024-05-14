from django.apps import AppConfig
from django_typer.utils import register_command_extensions


class Adapter1Config(AppConfig):
    name = "django_typer.tests.apps.adapter0"
    label = name.replace(".", "_")
    verbose_name = "Adapter 0"

    def ready(self):
        from .management import adapters

        register_command_extensions(adapters)
