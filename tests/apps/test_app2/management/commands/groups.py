from django.conf import settings
from django.utils.translation import gettext_lazy as _
from typer import Argument, Option
import typing as t

from django_typer.management import command, group, initialize
from django_typer import types
from tests.apps.test_app.management.commands.groups import (
    Command as GroupsCommand,
)


class Command(GroupsCommand, epilog="Overridden from test_app."):
    help = "Test groups command inheritance."

    precision = 2
    verbosity = 1

    suppressed_base_arguments = ["--version"]

    setting_name: str

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
    @GroupsCommand.string.case.command()
    def upper(self) -> str:
        assert self.__class__ is Command
        return super().upper(0, None)

    @GroupsCommand.string.command()
    def strip(self):
        """Strip white space off the ends of the string"""
        assert self.__class__ is Command
        return self.op_string.strip()

    @group()
    def setting(
        self, setting: t.Annotated[str, Argument(help=_("The setting variable name."))]
    ):
        """
        Get or set Django settings.
        """
        assert self.__class__ is Command
        self.setting_name = setting

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
            return getattr(settings, self.setting_name, None)
        return getattr(settings, self.setting_name)
