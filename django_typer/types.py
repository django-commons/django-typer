
import sys
from pathlib import Path
from typing import Annotated

from django.apps import AppConfig
from typer import Option, echo

_common_panel = 'Django'


def print_version(context, option, value):
    if value:
        echo(context.django_command.get_version())
        sys.exit()


Version = Annotated[
    bool,
    Option(
        '--version',
        help="Show program's version number and exit.",
        callback=print_version,
        is_eager=True,
        rich_help_panel=_common_panel
    )
]

Verbosity = Annotated[
    int,
    Option(
        help=(
            "Verbosity level; 0=minimal output, 1=normal output, "
            "2=verbose output, 3=very verbose output"
        ),
        show_choices=True,
        min=0,
        max=3,
        rich_help_panel=_common_panel
    )
]

Settings = Annotated[
    str,
    Option(
        help=(
            'The Python path to a settings module, e.g. '
            '"myproject.settings.main". If this isn\'t provided, the '
            'DJANGO_SETTINGS_MODULE environment variable will be used.'
        ),
        rich_help_panel=_common_panel
    )
]

PythonPath = Annotated[
    Path,
    Option(
        help=(
            'A directory to add to the Python path, e.g. '
            '"/home/djangoprojects/myproject".'
        ),
        rich_help_panel=_common_panel
    )
]

Traceback = Annotated[
    bool,
    Option(
        '--traceback',
        help=('Raise on CommandError exceptions'),
        rich_help_panel=_common_panel
    )
]

NoColor = Annotated[
    bool,
    Option(
        '--no-color',
        help=('Don\'t colorize the command output.'),
        rich_help_panel=_common_panel
    )
]

ForceColor = Annotated[
    bool,
    Option(
        '--force-color',
        help=('Force colorization of the command output.'),
        rich_help_panel=_common_panel
    )
]

SkipChecks = Annotated[
    bool,
    Option(
        '--skip-checks',
        help=('Skip system checks.'),
        rich_help_panel=_common_panel
    )
]
