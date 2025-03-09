from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, register
from django_typer.utils import register_command_plugins


@register()
def test_check(app_configs, **kwargs):
    errors = []
    if getattr(settings, "DJANGO_TYPER_FAIL_CHECK", False):
        errors.append(
            Error(
                "Test check error",
                hint="Error thrown because settings_fail_check was used.",
                obj=settings,
                id="test_app.E001",
            )
        )
    return errors


class TestAppConfig(AppConfig):
    name = "tests.apps.test_app"
    label = "test_app"
    verbose_name = "Test App"

    def ready(self):
        if getattr(settings, "DJANGO_TYPER_THROW_TEST_EXCEPTION", False):
            raise Exception("Test ready exception")

        from .management import extensions

        register_command_plugins(extensions)
