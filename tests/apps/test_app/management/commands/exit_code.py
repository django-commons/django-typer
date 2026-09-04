import typer

from django_typer.management import TyperCommand


class Command(TyperCommand):
    help = "Raises typer.Exit with the given code"

    def handle(self, code: int = 0):
        assert self.__class__ is Command
        raise typer.Exit(code)
