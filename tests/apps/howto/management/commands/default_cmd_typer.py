from django_typer.management import Typer

app = Typer()


@app.command(name="subcommand1")
def handle():
    return "handle"


@app.command()
def subcommand2():
    return "subcommand2"


@app.command()
def subcommand3():
    return "subcommand3"
