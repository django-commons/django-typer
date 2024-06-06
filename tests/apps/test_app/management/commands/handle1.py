from django_typer.management import command

from .handle import Command as Handle


class Command(Handle):
    help = "Test various forms of handle override."

    @command()
    def handle(self) -> str:
        assert self.__class__ is Command
        return "handle1"
