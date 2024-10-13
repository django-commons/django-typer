from django.apps import AppConfig

from django_typer.utils import register_command_plugins


class Files1Config(AppConfig):
    name = "tests.apps.examples.plugins.files1"
    label = name.replace(".", "_")

    def ready(self):
        from .management import plugins

        register_command_plugins(plugins)
