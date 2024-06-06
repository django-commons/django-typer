from django.core.management import CommandError

from django_typer.management import TyperCommand, command
from tests.utils import log_django_parameters


class Command(TyperCommand):
    help = "Test that django parameters work as expected"

    @command()
    def cmd1(self, throw: bool = False):
        assert self.__class__ is Command
        log_django_parameters(self)
        if throw:
            raise CommandError("Test Exception")

    @command()
    def cmd2(self, throw: bool = False):
        assert self.__class__ is Command
        log_django_parameters(self)
        if throw:
            raise CommandError("Test Exception")
