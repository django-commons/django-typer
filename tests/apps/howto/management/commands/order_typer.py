from django_typer.management import Typer, DTGroup
from click import Context
import typing as t


class AlphabetizeCommands(DTGroup):
    def list_commands(self, ctx: Context) -> t.List[str]:
        return list(sorted(self.commands.keys()))


app = Typer(cls=AlphabetizeCommands)

d_app = Typer(cls=AlphabetizeCommands)
app.add_typer(d_app, name="d")


@app.command()
def b():
    print("b")


@app.command()
def a():
    print("a")


@d_app.callback()
def d():
    print("d")


@d_app.command()
def f():
    print("f")


@d_app.command()
def e():
    print("e")


@app.command()
def c():
    print("c")
