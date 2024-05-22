from django.apps import AppConfig


class BasicExamplesConfig(AppConfig):
    name = "django_typer.tests.apps.examples.basic"
    label = name.replace(".", "_")
    verbose_name = "Basic Examples"
