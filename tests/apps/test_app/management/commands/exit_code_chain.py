import typer

from django_typer.management import TyperCommand, command


class Command(TyperCommand, chain=True):
    help = "A chained command whose second subcommand raises typer.Exit"

    @command()
    def a(self):
        assert self.__class__ is Command
        print("a ran")

    @command()
    def b(self, code: int = 0):
        assert self.__class__ is Command
        raise typer.Exit(code)
