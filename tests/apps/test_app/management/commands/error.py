from typing import Annotated

from typer import Option

from django_typer.management import TyperCommand


class Command(TyperCommand):
    help = "Test usage error behavior."

    def handle(
        self,
        arg1: int,
        flag1: bool = False,
        opt1: Annotated[int, Option(help="An option")] = 5,
    ):
        assert self.__class__ is Command
