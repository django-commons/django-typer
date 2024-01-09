import typing as t

from typer import Argument

from django_typer import command, initialize, types
from django_typer.tests.test_app.management.commands.groups import (
    Command as GroupsCommand,
)


class Command(GroupsCommand, add_completion=False, epilog="Overridden from test_app."):
    help = "Test groups command inheritance."

    precision = 2
    verbosity = 1

    @initialize()
    def init(self, verbosity: types.Verbosity = verbosity):
        """
        Initialize the command.
        """
        assert self.__class__ is Command
        self.verbosity = verbosity

    @command()
    def echo(
        self,
        message: str,
        echoes: t.Annotated[
            int, Argument(help="Number of times to echo the message.")
        ] = 1,
    ):
        """
        Echo the given message the given number of times.
        """
        assert self.__class__ is Command
        return " ".join([message] * echoes)

    # test override base class command and remove arguments
    @GroupsCommand.case.command()
    def upper(self):
        return super().upper(0, None)

    @GroupsCommand.string.command()
    def strip(self):
        """Strip white space off the ends of the string"""
        return self.op_string.strip()
