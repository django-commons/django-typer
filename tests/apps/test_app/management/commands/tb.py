import sys

import click
from django.core.management.base import CommandError

from django_typer.management import TyperCommand, command


class Command(TyperCommand):
    help = "Test traceback scenarios."

    @command()
    def error(self, throw_command: bool = False, throw_other: bool = False):
        assert self.__class__ is Command
        if throw_command and throw_other:
            raise click.exceptions.UsageError(
                "--throw-command and --throw-other are mutually exclusive."
            )
        if throw_command:
            raise CommandError("This command failed!")
        if throw_other:
            raise RuntimeError("This command threw an unexpected error!")

    @command()
    def exit(self, code: int = 0):
        assert self.__class__ is Command
        sys.exit(code)
