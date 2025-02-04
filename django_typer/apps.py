"""
Django Typer app config. This module includes settings check and rich traceback
installation logic.
"""

import inspect
import os
import sys
import typing as t

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import CheckMessage, register
from django.core.checks import Warning as CheckWarning

from .config import traceback_config

tb_config = traceback_config()
try_install = isinstance(tb_config, dict) and not tb_config.get("no_install", False)

if try_install:
    try:
        import rich  # pyright: ignore[reportMissingImports]
        from rich import traceback  # pyright: ignore[reportMissingImports]

        from django_typer import patch

        patch.apply()

        from typer import main as typer_main

        # install rich tracebacks if we've been configured to do so (default)
        assert isinstance(tb_config, dict)
        no_color = "NO_COLOR" in os.environ
        force_color = "FORCE_COLOR" in os.environ
        traceback.install(
            console=tb_config.pop(
                "console",
                (
                    rich.console.Console(
                        stderr=True,
                        no_color=no_color,
                        force_terminal=(
                            False if no_color else force_color if force_color else None
                        ),
                    )
                    if no_color or force_color
                    else None
                ),
            ),
            **{
                param: value
                for param, value in tb_config.items()
                if param in set(inspect.signature(traceback.install).parameters.keys())
            },
        )
        # typer installs its own exception hook and it falls back to the sys hook - depending
        # on when typer was imported it may have the original fallback system hook or our
        # installed rich one - we patch it here to make sure!
        typer_main._original_except_hook = sys.excepthook

    except ImportError:
        pass


@register("settings")
def check_traceback_config(app_configs, **kwargs) -> t.List[CheckMessage]:
    """
    A system check that validates that the traceback config is valid and
    contains only the expected parameters.
    """
    warnings: t.List[CheckMessage] = []
    if try_install:
        assert isinstance(tb_config, dict)
        try:
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
        except ImportError:
            pass
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
