from django_typer.management import TyperCommand, DTGroup, command, group
from click import Context


class ReverseAlphaCommands(DTGroup):
    def list_commands(self, ctx: Context) -> list[str]:
        return list(sorted(self.commands.keys(), reverse=True))


class Command(TyperCommand, cls=ReverseAlphaCommands):
    @command()
    def a(self):
        print("a")

    @command()
    def b(self):
        print("b")

    @command()
    def c(self):
        print("c")

    @group(cls=ReverseAlphaCommands)
    def d(self):
        print("d")

    @d.command()
    def e(self):
        print("e")

    @d.command()
    def f(self):
        print("f")
