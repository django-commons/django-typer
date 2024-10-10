from django_typer.management import Typer, DTGroup
from click import Context


class ReverseAlphaCommands(DTGroup):
    def list_commands(self, ctx: Context) -> list[str]:
        return list(sorted(self.commands.keys(), reverse=True))


app = Typer(cls=ReverseAlphaCommands)

d_app = Typer(cls=ReverseAlphaCommands)
app.add_typer(d_app)


@app.command()
def a():
    print("a")


@app.command()
def b():
    print("b")


@app.command()
def c():
    print("c")


@d_app.callback(cls=ReverseAlphaCommands)
def d():
    print("d")


@d_app.command()
def e():
    print("e")


@d_app.command()
def f():
    print("f")
