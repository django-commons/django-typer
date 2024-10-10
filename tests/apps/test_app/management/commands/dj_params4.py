from typing import Annotated

from django.core.management import CommandError
from typer import Option

from django_typer.management import TyperCommand, command
from django_typer import types
from tests.utils import log_django_parameters


class Command(TyperCommand):
    help = "Test that django parameters work as expected"

    @command(epilog="epilog")
    def handle(
        self,
        throw: bool = False,
        verbosity: types.Verbosity = 1,
        traceback: Annotated[
            bool,
            Option(
                help=("Raise on CommandError exceptions"),
                rich_help_panel=types.COMMON_PANEL,
            ),
        ] = True,  # this should change the default!
    ):
        assert self.__class__ is Command
        log_django_parameters(self, verbosity=verbosity, traceback=traceback)
        if throw:
            raise CommandError("Test Exception")
