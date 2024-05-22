from django.apps import AppConfig


class PollsConfig(AppConfig):
    name = "django_typer.tests.apps.examples.polls"
    label = name.replace(".", "_")
