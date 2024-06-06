from django.apps import AppConfig

from django_typer.utils import register_command_plugins


class MyAppConfig(AppConfig):
    name = "tests.apps.examples.plugins.my_app"
    label = name.replace(".", "_")

    def ready(self):
        from .management import plugins

        register_command_plugins(plugins)
