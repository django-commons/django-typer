from django.apps import AppConfig


class PollsConfig(AppConfig):
    name = 'django_typer.tests.polls'
    label = name.replace('.', '_')
