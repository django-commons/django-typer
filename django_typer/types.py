"""
Common types for command line argument specification.
"""

import sys
from pathlib import Path
from typing import Annotated, Optional

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
