from django.apps import AppConfig
from django_typer.utils import register_command_extensions


class MyAppConfig(AppConfig):
    name = "django_typer.tests.apps.examples.extensions.my_app"
    label = name.replace(".", "_")

    def ready(self):
        from .management import extensions

        register_command_extensions(extensions)
