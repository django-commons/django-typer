from django_typer.management import Typer

from .upstream_typer import app as upstream

# pass the upstream app as the first positional argument to Typer
app = Typer(upstream)


# override init
@app.callback()
def init():
    return "downstream:init"


# override sub1
@app.command()
def sub1():
    return "downstream:sub1"


# add a 3rd top level command
@app.command()
def sub3():
    return "downstream:sub3"


# add a new subcommand to grp1
@app.grp1.command()
def grp1_cmd2():
    return "downstream:grp1_cmd2"
