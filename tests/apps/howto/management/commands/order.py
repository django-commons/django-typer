import typing as t
from django_typer.management import TyperCommand, DTGroup, command, group
from click import Context


class AlphabetizeCommands(DTGroup):
    def list_commands(self, ctx: Context) -> t.List[str]:
        return list(sorted(self.commands.keys()))


class Command(TyperCommand, cls=AlphabetizeCommands):
    @command()
    def b(self):
        print("b")

    @command()
    def a(self):
        print("a")

    @group(cls=AlphabetizeCommands)
    def d(self):
        print("d")

    @d.command()
    def f(self):
        print("f")

    @d.command()
    def e(self):
        print("e")

    @command()
    def c(self):
        print("c")
