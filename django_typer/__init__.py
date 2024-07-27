r"""
::

      ___ _                           _____
     /   (_) __ _ _ __   __ _  ___   /__   \_   _ _ __   ___ _ __
    / /\ / |/ _` | '_ \ / _` |/ _ \    / /\/ | | | '_ \ / _ \ '__|
   / /_//| | (_| | | | | (_| | (_) |  / /  | |_| | |_) |  __/ |
  /___,'_/ |\__,_|_| |_|\__, |\___/   \/    \__, | .__/ \___|_|
       |__/             |___/               |___/|_|


django-typer_ provides an extension class, :class:`~django_typer.TyperCommand`, to the
BaseCommand_ class that melds the Typer_/click_ infrastructure with
the Django_ infrastructure. The result is all the ease of specifying commands, groups
and options and arguments using Typer_ and click_ in a way that feels like and is
interface compatible with Django_'s BaseCommand_ This should enable a smooth transition
for existing Django_ commands and an intuitive feel for implementing new commands.

django-typer_ also supports shell completion for bash_, zsh_, fish_ and powershell_ and
extends that support to native Django_ management commands as well.


The goal of django-typer_ is to provide full Typer_ style functionality while maintaining
compatibility with the Django management command system. This means that the BaseCommand_
interface is preserved and the Typer_ interface is added on top of it. This means that
this code base is more robust to changes in the Django management command system - because
most of the base class functionality is preserved but many Typer_ and click_ internals are
used directly to achieve this. We rely on robust CI to catch breaking changes upstream and
keep a tight version lock on Typer.
"""

# WARNING - these imports are going away in version 3!
# import them from django_typer.management directly
from .management import (
    CommandNode,  # noqa: F401
    Context,  # noqa: F401
    DjangoTyperMixin,  # noqa: F401
    DTCommand,  # noqa: F401
    DTGroup,  # noqa: F401
    Typer,  # noqa: F401
    TyperCommand,  # noqa: F401
    callback,  # noqa: F401
    command,  # noqa: F401
    get_command,  # noqa: F401
    group,  # noqa: F401
    initialize,  # noqa: F401
    model_parser_completer,  # noqa: F401
)

VERSION = (2, 2, 0)

__title__ = "Django Typer"
__version__ = ".".join(str(i) for i in VERSION)
__author__ = "Brian Kohan"
__license__ = "MIT"
__copyright__ = "Copyright 2023-2024 Brian Kohan"
