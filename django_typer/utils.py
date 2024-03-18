"""
A collection of useful utilities.
"""

import os
import shutil
import sys
import typing as t
from pathlib import Path
from threading import local

from django.conf import settings

# DO NOT IMPORT ANYTHING FROM TYPER HERE - SEE patch.py


def get_usage_script(script: t.Optional[str] = None) -> t.Union[Path, str]:
    """
    Return the script name if it is on the path or the absolute path to the script
    if it is not.

    :param script: The script name to check. If None the current script is used.
    :return: The script name or the relative path to the script from cwd.
    """
    cmd_pth = Path(script or sys.argv[0])
    if shutil.which(cmd_pth.name):
        return cmd_pth.name
    try:
        return cmd_pth.absolute().relative_to(Path(os.getcwd()))
    except ValueError:
        return cmd_pth.absolute()


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


_command_context = local()


def get_current_command() -> t.Optional["TyperCommand"]:  # type: ignore
    """
    Returns the current typer command. This can be used as a way to
    access the current command object from anywhere if we are executing
    inside of one from higher on the stack. We primarily need this because certain
    monkey patches are required in typer code - namely for enabling/disabling
    color based on configured parameters.

    This function is thread safe.

    This is analogous to click's get_current_context but for
    command execution.

    :return: The current typer command or None if there is no active command.
    """
    try:
        return t.cast("TyperCommand", _command_context.stack[-1])  # type: ignore
    except (AttributeError, IndexError):
        pass
    return None


T = t.TypeVar("T")  # pylint: disable=C0103


def with_typehint(baseclass: t.Type[T]) -> t.Type[T]:
    """
    Type hinting mixin inheritance is really annoying. The current
    canonical way is to use Protocols but this is prohibitive when
    the super classes already exist and are extensive. All we're
    trying to do is let our type checker know about super() methods
    etc - this is a simple way to do that.
    """
    if t.TYPE_CHECKING:
        return baseclass  # pragma: no cover
    return object  # type: ignore
