from django.apps import AppConfig
from django_typer.utils import register_command_extensions


class TestApp2Config(AppConfig):
    name = "django_typer.tests.apps.test_app2"
    label = name.replace(".", "_")
    verbose_name = "Test App2"
