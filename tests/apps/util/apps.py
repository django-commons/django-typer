from django.apps import AppConfig


class UtilConfig(AppConfig):
    name = "tests.apps.util"
    label = name.replace(".", "_")
