"""
A collection of useful utilities.
"""

import importlib
import inspect
import os
import pkgutil
import shutil
import sys
import typing as t
from functools import partial
from pathlib import Path
from threading import local
from types import MethodType, ModuleType

from django.conf import settings

# DO NOT IMPORT ANYTHING FROM TYPER HERE - SEE patch.py

__all__ = [
    "get_usage_script",
    "traceback_config",
    "get_current_command",
    "with_typehint",
    "register_command_extensions",
    "called_from_module",
    "called_from_command_definition",
]


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


def get_current_command() -> t.Optional["TyperCommand"]:  # type: ignore  # noqa: F821
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
        return t.cast("TyperCommand", _command_context.stack[-1])  # type: ignore  # noqa: F821
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


_command_extensions: t.Dict[str, t.List[ModuleType]] = {}


def register_command_extensions(
    package: ModuleType, commands: t.Optional[t.List[str]] = None
):
    """
    Register a command extension for the given command within the given package.

    For example, use this in your AppConfig's ready() method:

    .. code-block:: python

        from django.apps import AppConfig
        from django_typer.utils import register_command_extensions


        class MyAppConfig(AppConfig):
            name = "myapp"

            def ready(self):
                from .management import extensions

                register_command_extensions(extensions)


    :param package: The package the command extension module resides in
    :param commands: The names of the commands/modules, if not provided, all modules
        in the package will be registered as extensions
    """
    commands = commands or [
        module[1].split(".")[-1]
        for module in pkgutil.iter_modules(package.__path__, f"{package.__name__}.")
    ]
    for command in commands:
        _command_extensions.setdefault(command, [])
        if package not in _command_extensions[command]:
            _command_extensions[command].append(package)


def _load_command_extensions(command: str) -> int:
    """
    Load any extensions for the given command by loading the registered
    modules in registration order.

    :param command: The name of the command
    :return: The number of extensions loaded.
    """
    extensions = _command_extensions.get(command, [])
    if extensions:
        for ext_pkg in reversed(extensions):
            try:
                importlib.import_module(f"{ext_pkg.__name__}.{command}")
            except (ImportError, ModuleNotFoundError) as err:
                raise ValueError(
                    f"No extension module was found for command {command} in {ext_pkg.__path__}."
                ) from err
        # we only want to do this once
        del _command_extensions[command]
    return len(extensions)


def _check_call_frame(frame_name: str) -> bool:
    """
    Returns True if the stack frame one frame above where this function has the given
    name.

    :param frame_name: The name of the frame to check for
    """
    frame = inspect.currentframe()
    for _ in range(0, 2):
        if not frame:
            break
        frame = frame.f_back
    if frame:
        return frame.f_code.co_name == frame_name
    return False


called_from_module = partial(_check_call_frame, "<module>")
called_from_command_definition = partial(_check_call_frame, "Command")


def is_method(
    func_or_params: t.Optional[t.Union[t.Callable[..., t.Any], t.List[str]]],
) -> t.Optional[bool]:
    """
    This logic is used to to determine if a function should be bound as a method
    or not. Right now django-typer will treat module scope functions as methods
    when binding to command classes if they have a first argument named 'self'.

    :param func: The function to check or a list of parameter names, or None
    :return: True if the function should be considered a method, False if not and None
        if undetermined.
    """
    ##############
    # Remove when python 3.8 support is dropped
    func_or_params = getattr(func_or_params, "__func__", func_or_params)
    ##############
    if func_or_params:
        params = (
            list(inspect.signature(func_or_params).parameters)
            if callable(func_or_params)
            else func_or_params
        )
        if params:
            return params[0] == "self"
        return isinstance(func_or_params, MethodType)
    return None
