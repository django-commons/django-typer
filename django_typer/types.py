"""
Common types for command line argument specification.
"""

# pylint: disable=pointless-string-statement, line-too-long

import sys
from pathlib import Path
from typing import Optional, cast

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

from django.core.management import CommandError
from django.utils.translation import gettext_lazy as _
from typer import Option

COMMON_PANEL = "Django"


def print_version(context, _, value):
    """
    A callback to run the get_version() routine of the
    command when --version is specified.
    """
    if value:
        context.django_command.stdout.write(context.django_command.get_version())
        sys.exit()


def set_no_color(context, param, value):
    """
    If the value was provided set it on the command.
    """
    if value:
        context.django_command.no_color = value
        if context.params.get("force_color", False):
            raise CommandError(
                _("The --no-color and --force-color options can't be used together.")
            )
    return value


def set_force_color(context, param, value):
    """
    If the value was provided set it on the command.
    """
    if value:
        context.django_command.force_color = value
    return value


Version = Annotated[
    bool,
    Option(
        "--version",
        help=cast(str, _("Show program's version number and exit.")),
        callback=print_version,
        is_eager=True,
        rich_help_panel=COMMON_PANEL,
    ),
]
"""
The type hint for the 
`Django --version option <https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#django.core.management.BaseCommand.get_version>`_.

The --version option is included by default and behaves the same as on BaseCommand_.
"""


Verbosity = Annotated[
    int,
    Option(
        help=cast(
            str,
            _(
                "Verbosity level; 0=minimal output, 1=normal output, "
                "2=verbose output, 3=very verbose output"
            ),
        ),
        show_choices=True,
        min=0,
        max=3,
        rich_help_panel=COMMON_PANEL,
    ),
]
"""
The type hint for the 
`Django --verbosity option <https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-verbosity>`_.
:class:`~django_typer.TyperCommand` does not include the verbosity option by default, but it can be
added to the command like so if needed.

.. code-block:: python
    
        from django_typer.types import Verbosity
    
        def handle(self, verbosity: Verbosity = 1):
            ...
"""

Settings = Annotated[
    str,
    Option(
        help=cast(
            str,
            _(
                "The Python path to a settings module, e.g. "
                '"myproject.settings.main". If this isn\'t provided, the '
                "DJANGO_SETTINGS_MODULE environment variable will be used."
            ),
        ),
        rich_help_panel=COMMON_PANEL,
    ),
]
"""
The type hint for the 
`Django --settings option <https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-settings>`_.

The --settings option is included by default and behaves the same as on BaseCommand_ use it to
specify or override the settings module to use.
"""


PythonPath = Annotated[
    Optional[Path],
    Option(
        help=cast(
            str,
            _(
                "A directory to add to the Python path, e.g. "
                '"/home/djangoprojects/myproject".'
            ),
        ),
        rich_help_panel=COMMON_PANEL,
    ),
]
"""
The type hint for the 
`Django --pythonpath option <https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-pythonpath>`_.

The --pythonpath option is included by default and behaves the same as on BaseCommand_ use it to
specify a directory to add to the Python sys path.
"""


Traceback = Annotated[
    bool,
    Option(
        "--traceback",
        help=cast(str, _("Raise on CommandError exceptions")),
        rich_help_panel=COMMON_PANEL,
    ),
]
"""
The type hint for the 
`Django --traceback option <https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-traceback>`_.

The --traceback option is included by default and behaves the same as on BaseCommand_ use it to
allow CommandError exceptions to propagate out of the command and produce a stack trace.
"""


NoColor = Annotated[
    bool,
    Option(
        "--no-color",
        help=cast(str, _("Don't colorize the command output.")),
        is_eager=True,
        callback=set_no_color,
        rich_help_panel=COMMON_PANEL,
    ),
]
"""
The type hint for the 
`Django --no-color option <https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-no-color>`_.

The --no-color option is included by default and behaves the same as on BaseCommand_ use it to
force disable colorization of the command. You can check the supplied value of --no-color by
checking the no_color attribute of the command instance.
"""

ForceColor = Annotated[
    bool,
    Option(
        "--force-color",
        help=cast(str, _("Force colorization of the command output.")),
        is_eager=True,
        callback=set_force_color,
        rich_help_panel=COMMON_PANEL,
    ),
]
"""
The type hint for the 
`Django --force-color option <https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-force-color>`_.

The --force-color option is included by default and behaves the same as on BaseCommand_ use it to
force colorization of the command. You can check the supplied value of --force-color by checking
the force_color attribute of the command instance.
"""

SkipChecks = Annotated[
    bool,
    Option(
        "--skip-checks",
        help=cast(str, _("Skip system checks.")),
        rich_help_panel=COMMON_PANEL,
    ),
]
"""
The type hint for the 
`Django --skip-checks option <https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-skip-checks>`_.

The --skip-checks option is included by default and behaves the same as on BaseCommand_ use it to
skip system checks.
"""
