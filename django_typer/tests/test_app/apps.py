from django.apps import AppConfig


class TestAppConfig(AppConfig):
    name = 'django_typer.tests.test_app'
    label = name.replace('.', '_')
    verbose_name = "Test App"

