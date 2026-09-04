"""
Exercise how typer.Exit, typer.Abort, interrupts and sys.exit leave a compound
command - see issue #318.
"""

import sys

import typer

from django_typer.management import TyperCommand, command


class Command(TyperCommand):
    @command()
    def exit(self, code: int = 0):
        raise typer.Exit(code)

    @command()
    def abort(self):
        raise typer.Abort()

    @command()
    def interrupt(self):
        raise KeyboardInterrupt()

    @command()
    def eof(self):
        # what a prompt raises when input has ended
        raise EOFError()

    @command()
    def sysexit(self, code: int = 0):
        sys.exit(code)
