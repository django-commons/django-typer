from typing import Optional

import typer

from django_typer.management import TyperCommand, command


class Command(TyperCommand):
    help = "Test typer echo/secho wrappers."

    @command()
    def echo_test(
        self,
        message: str,
        color: Optional[str] = None,
        error: Optional[bool] = False,
        nl: Optional[bool] = True,
    ):
        assert self.__class__ is Command
        if color:
            self.echo(typer.style(message, fg=color), nl=nl, err=error)
        else:
            self.echo(message, nl=nl, err=error)

    @command()
    def secho_test(
        self,
        message: str,
        color: Optional[str] = None,
        error: Optional[bool] = False,
        nl: Optional[bool] = True,
    ):
        assert self.__class__ is Command
        self.secho(message, nl=nl, err=error, fg=color)
