import typing as t

from django.conf import settings


def traceback_config() -> t.Union[bool, t.Dict[str, t.Any]]:
    """
    Fetch the rich traceback installation parameters from our settings. By default
    rich tracebacks are on with show_locals = True. If the config is set to False
    or None rich tracebacks will not be installed even if the library is present.

    This allows us to have a common traceback configuration for all commands. If rich
    tracebacks are managed separately this setting can also be switched off.
    """
    cfg = getattr(settings, "DT_RICH_TRACEBACK_CONFIG", {"show_locals": True})
    if cfg:
        return {"show_locals": True, **cfg}
    return bool(cfg)
