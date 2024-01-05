import typing as t

from typer import Argument

from django_typer import callback, command, types
from django_typer.tests.test_app.management.commands.groups import (
    Command as GroupsCommand,
)


class Command(GroupsCommand):
    help = "Test groups command inheritance."

    precision = 2
    verbosity = 1

    @callback()
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
        Echo the given message.
        """
        assert self.__class__ is Command
        return " ".join([message] * echoes)
