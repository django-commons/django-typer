import typing as t

from django.conf import settings


def traceback_config() -> t.Dict[str, t.Any]:
    """
    Fetch the rich traceback installation parameters from our settings. By default
    rich tracebacks are on with show_locals = True. If the config is set to False
    or None rich tracebacks will not be installed even if the library is present.

    This allows us to have a common traceback configuration for all commands. If rich
    tracebacks are managed separately this setting can also be switched off.
    """
    default = {"show_locals": False}
    cfg = getattr(settings, "DT_RICH_TRACEBACK_CONFIG", default) or default
    if cfg is True:
        return default
    return cfg


def show_locals() -> t.Optional[bool]:
    """
    Return the show_locals parameter from the rich traceback configuration.
    """
    return traceback_config().get("show_locals", None)


def use_rich_tracebacks() -> bool:
    """
    Return true if rich tracebacks should be installed, False otherwise.
    """
    from .utils import rich_installed

    cfg = getattr(settings, "DT_RICH_TRACEBACK_CONFIG", {"show_locals": False})
    return rich_installed and (
        (isinstance(cfg, dict) and not cfg.get("no_install", False)) or cfg is True
    )
