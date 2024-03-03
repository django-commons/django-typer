from django.apps import AppConfig


class ExamplesConfig(AppConfig):
    name = "django_typer.tests.examples"
    label = name.replace(".", "_")
    verbose_name = "Examples"
