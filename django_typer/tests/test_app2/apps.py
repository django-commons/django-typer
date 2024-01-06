from django.apps import AppConfig

class TestApp2Config(AppConfig):
    name = "django_typer.tests.test_app2"
    label = name.replace(".", "_")
    verbose_name = "Test App2"
