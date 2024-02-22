"""
Common types for command line argument specification.
"""

# pylint: disable=pointless-string-statement

import sys
from pathlib import Path
from typing import Any, Callable, Optional

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

from django.core.management import CommandError
from django.core.management.color import Style as ColorStyle
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


"""
https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#django.core.management.BaseCommand.get_version
"""
Version = Annotated[
    bool,
    Option(
        "--version",
        help=_("Show program's version number and exit."),
        callback=print_version,
        is_eager=True,
        rich_help_panel=COMMON_PANEL,
    ),
]

"""
https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-verbosity
"""
Verbosity = Annotated[
    int,
    Option(
        help=_(
            "Verbosity level; 0=minimal output, 1=normal output, "
            "2=verbose output, 3=very verbose output"
        ),
        show_choices=True,
        min=0,
        max=3,
        rich_help_panel=COMMON_PANEL,
    ),
]

"""
https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-settings
"""
Settings = Annotated[
    str,
    Option(
        help=_(
            "The Python path to a settings module, e.g. "
            '"myproject.settings.main". If this isn\'t provided, the '
            "DJANGO_SETTINGS_MODULE environment variable will be used."
        ),
        rich_help_panel=COMMON_PANEL,
    ),
]

"""
https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-pythonpath
"""
PythonPath = Annotated[
    Optional[Path],
    Option(
        help=_(
            "A directory to add to the Python path, e.g. "
            '"/home/djangoprojects/myproject".'
        ),
        rich_help_panel=COMMON_PANEL,
    ),
]

"""
https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-traceback
"""
Traceback = Annotated[
    bool,
    Option(
        "--traceback",
        help=_("Raise on CommandError exceptions"),
        rich_help_panel=COMMON_PANEL,
    ),
]

"""
https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-no-color
"""
NoColor = Annotated[
    bool,
    Option(
        "--no-color",
        help=_("Don't colorize the command output."),
        is_eager=True,
        callback=set_no_color,
        rich_help_panel=COMMON_PANEL,
    ),
]


"""
https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-force-color
"""
ForceColor = Annotated[
    bool,
    Option(
        "--force-color",
        help=_("Force colorization of the command output."),
        is_eager=True,
        callback=set_force_color,
        rich_help_panel=COMMON_PANEL,
    ),
]

"""
https://docs.djangoproject.com/en/stable/ref/django-admin/#cmdoption-skip-checks
"""
SkipChecks = Annotated[
    bool,
    Option(
        "--skip-checks", help=_("Skip system checks."), rich_help_panel=COMMON_PANEL
    ),
]


class Style(ColorStyle):
    """
    For type hinting.
    """

    ERROR: Callable[[Any], str]
    ERROR_OUTPUT: Callable[[Any], str]
    HTTP_BAD_REQUEST: Callable[[Any], str]
    HTTP_INFO: Callable[[Any], str]
    HTTP_NOT_FOUND: Callable[[Any], str]
    HTTP_NOT_MODIFIED: Callable[[Any], str]
    HTTP_REDIRECT: Callable[[Any], str]
    HTTP_SERVER_ERROR: Callable[[Any], str]
    HTTP_SUCCESS: Callable[[Any], str]
    MIGRATE_HEADING: Callable[[Any], str]
    MIGRATE_LABEL: Callable[[Any], str]
    NOTICE: Callable[[Any], str]
    SQL_COLTYPE: Callable[[Any], str]
    SQL_FIELD: Callable[[Any], str]
    SQL_KEYWORD: Callable[[Any], str]
    SQL_TABLE: Callable[[Any], str]
    SUCCESS: Callable[[Any], str]
    WARNING: Callable[[Any], str]
