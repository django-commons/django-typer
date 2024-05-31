from django.apps import AppConfig


class TestApp2Config(AppConfig):
    name = "django_typer.tests.apps.test_app2"
    label = name.replace(".", "_")
    verbose_name = "Test App2"
