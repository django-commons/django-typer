import typing as t

from typer import Argument, Option

from django_typer import TyperCommand, command


class Command(TyperCommand):

    @command()
    def option1(self, flag: bool = False):
        pass

    @command()
    def option2(self, name: str = "world"):
        pass

    @command()
    def option3(self, name: t.Annotated[str, Option(help="The name of the thing")]):
        pass

    @command()
    def arg1(self, int_arg: int):
        pass

    @command()
    def arg2(self, int_arg: t.Annotated[int, Argument(help="An integer argument")]):
        pass
