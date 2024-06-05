from django.apps import AppConfig


class BasicExamplesConfig(AppConfig):
    name = "tests.apps.examples.basic"
    label = name.replace(".", "_")
    verbose_name = "Basic Examples"
