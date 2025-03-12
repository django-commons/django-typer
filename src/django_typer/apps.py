"""
Django Typer app config. This module includes settings check and rich traceback
installation logic.
"""

import inspect
import typing as t

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import CheckMessage, register
from django.core.checks import Warning as CheckWarning

from django_typer import patch

from .config import traceback_config, use_rich_tracebacks
from .utils import install_traceback

patch.apply()
install_traceback()


@register("settings")
def check_traceback_config(app_configs, **kwargs) -> t.List[CheckMessage]:
    """
    A system check that validates that the traceback config is valid and
    contains only the expected parameters.
    """

    warnings: t.List[CheckMessage] = []
    if use_rich_tracebacks():
        tb_config = traceback_config()
        from rich import traceback  # pyright: ignore[reportMissingImports]

        expected = {
            "no_install",
            "short",
            *inspect.signature(traceback.install).parameters.keys(),
        }
        unexpected = set(tb_config.keys()) - expected
        if unexpected:
            warnings.append(
                CheckWarning(
                    "DT_RICH_TRACEBACK_CONFIG",
                    hint="Unexpected parameters encountered: {keys}.".format(
                        keys=", ".join(unexpected)
                    ),
                    obj=settings.SETTINGS_MODULE,
                    id="django_typer.W001",
                )
            )
    return warnings


class DjangoTyperConfig(AppConfig):
    """
    Django Typer app config.
    """

    name = "django_typer"
    label = name
    verbose_name = "Django Typer"

    def ready(self):
        from django_typer.management import extensions
        from django_typer.utils import register_command_plugins

        register_command_plugins(extensions, ["shellcompletion"])
