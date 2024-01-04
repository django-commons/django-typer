from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Error, register


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
    name = "django_typer.tests.test_app"
    label = name.replace(".", "_")
    verbose_name = "Test App"
