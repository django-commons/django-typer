import typing as t
from django_typer import command
from .handle import Command as Handle


class Command(Handle):
    help = "Test various forms of handle override."

    @command()
    def handle(self) -> str:
        return "handle1"