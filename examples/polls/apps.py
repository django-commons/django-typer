from django.apps import AppConfig


class PollsConfig(AppConfig):
    name = "tests.apps.examples.polls"
    label = name.replace(".", "_")
