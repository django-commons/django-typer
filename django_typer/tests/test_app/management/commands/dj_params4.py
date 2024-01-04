from django.core.management import CommandError

from django_typer import TyperCommand, callback, command, types
from django_typer.tests.utils import log_django_parameters


class Command(TyperCommand):
    help = "Test that django parameters work as expected"

    @command(epilog="epilog")
    def handle(self, throw: bool = False, verbosity: types.Verbosity = 1):
        assert self.__class__ == Command
        log_django_parameters(self, verbosity=verbosity)
        if throw:
            raise CommandError("Test Exception")
