from django.apps import AppConfig


class MediaConfig(AppConfig):
    name = "tests.apps.examples.plugins.media1"
    label = name.replace(".", "_")
