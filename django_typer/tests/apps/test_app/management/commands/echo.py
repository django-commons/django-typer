from django_typer import TyperCommand, command
import typer
from typing import Optional


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
        self.secho(message, nl=nl, err=error, fg=color)
