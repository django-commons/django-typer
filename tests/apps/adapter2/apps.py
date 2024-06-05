from django.apps import AppConfig

from django_typer.utils import register_command_plugins


class Adapter2Config(AppConfig):
    name = "tests.apps.adapter2"
    label = "adapter2"
    verbose_name = "Adapter 2"

    def ready(self):
        from .management import adapters

        register_command_plugins(adapters, ["adapted2"])
