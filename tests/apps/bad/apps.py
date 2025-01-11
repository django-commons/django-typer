from django.apps import AppConfig
from django_typer.utils import register_command_plugins


class BadConfig(AppConfig):
    name = "tests.apps.bad"
    label = "bad"
    verbose_name = "Bad"

    def ready(self):
        from .management import extensions

        register_command_plugins(extensions, ["bad"])
