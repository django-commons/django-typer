from django.apps import AppConfig


class TyperExamplesConfig(AppConfig):
    name = "tests.apps.examples.typer"
    label = name.replace(".", "_")
    verbose_name = "Typer Examples"
