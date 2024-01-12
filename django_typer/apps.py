import inspect

from django.apps import AppConfig
from django.conf import settings
from django.core.checks import Warning, register
from django.utils.translation import gettext_lazy as _

from django_typer import traceback_config

try:
    import rich

    tb_config = traceback_config()
    if isinstance(tb_config, dict) and not tb_config.get("no_install", False):
        rich.traceback.install(
            **{
                param: value
                for param, value in tb_config.items()
                if param
                in set(inspect.signature(rich.traceback.install).parameters.keys())
            }
        )
except ImportError:
    rich = None


@register("settings")
def check_traceback_config(app_configs, **kwargs):
    warnings = []
    tb_cfg = traceback_config()
    if isinstance(tb_cfg, dict):
        if rich:
            expected = {
                "no_install",
                "short",
                *inspect.signature(rich.traceback.install).parameters.keys(),
            }
            unexpected = set(tb_cfg.keys()) - expected
            if unexpected:
                warnings.append(
                    Warning(
                        "DT_RICH_TRACEBACK_CONFIG",
                        hint=_("Unexpected parameters encountered: {keys}.").format(
                            keys=", ".join(unexpected)
                        ),
                        obj=settings.SETTINGS_MODULE,
                        id="django_typer.W001",
                    )
                )
    return warnings


from django import conf


class DjangoTyperConfig(AppConfig):
    name = "django_typer"
    label = name.replace(".", "_")
    verbose_name = "Django Typer"
