from django_typer.management import Typer

app = Typer()


@app.callback()
def init():
    return "upstream:init"


@app.command()
def sub1():
    return "upstream:sub1"


@app.command()
def sub2():
    return "upstream:sub2"


@app.group()
def grp1():
    return "upstream:grp1"


@app.grp1.command()
def grp1_cmd1():
    return "upstream:grp1_cmd1"
