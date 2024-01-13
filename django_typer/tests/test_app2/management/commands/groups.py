import typing as t

from django.conf import settings
from django.utils.translation import gettext_lazy as _
from typer import Argument, Option

from django_typer import command, group, initialize, types
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

    @group()
    def setting(
        self, setting: t.Annotated[str, Argument(help=_("The setting variable name."))]
    ):
        """
        Get or set Django settings.
        """
        assert self.__class__ is Command
        self.setting = setting

    @setting.command()
    def print(
        self,
        safe: t.Annotated[bool, Option(help=_("Do not assume the setting exists."))],
    ):
        """
        Print the setting value.
        """
        assert self.__class__ is Command
        if safe:
            return getattr(settings, self.setting, None)
        return getattr(settings, self.setting)
