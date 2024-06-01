from django.apps import AppConfig


class MediaConfig(AppConfig):
    name = "django_typer.tests.apps.examples.plugins.media1"
    label = name.replace(".", "_")
