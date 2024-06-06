from django.apps import AppConfig

from django_typer.utils import register_command_plugins


class Adapter1Config(AppConfig):
    name = "tests.apps.adapter1"
    label = "adapter1"
    verbose_name = "Adapter 1"

    def ready(self):
        from .management import adapters

        register_command_plugins(adapters)
