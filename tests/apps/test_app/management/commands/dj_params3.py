from django.core.management import CommandError

from django_typer.management import TyperCommand, command, initialize
from django_typer import types
from tests.utils import log_django_parameters


class Command(TyperCommand):
    help = "Test that django parameters work as expected"

    @initialize()
    def init(self, verbosity: types.Verbosity = 1):
        """
        The callback to initialize the command.
        """
        assert self.__class__ is Command
        self.verbosity = verbosity

    @command()
    def cmd1(self, throw: bool = False):
        assert self.__class__ is Command
        log_django_parameters(self, verbosity=self.verbosity)
        if throw:
            raise CommandError("Test Exception")

    @command()
    def cmd2(self, throw: bool = False):
        assert self.__class__ is Command
        log_django_parameters(self, verbosity=self.verbosity)
        if throw:
            raise CommandError("Test Exception")
