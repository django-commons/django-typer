from django_typer.management import Typer, TyperCommand
from django_typer.types import Verbosity

Command: TyperCommand

app = Typer()


_verbosity = None
_flag = None


@app.callback()
def init(verbosity: Verbosity = 0):
    global _verbosity
    _verbosity = verbosity


@app.command()
def main(name: str):
    return {"verbosity": _verbosity, "name": name}


grp2 = Typer()


@grp2.callback()
def init_grp1(flag: bool = False):
    global _flag
    _flag = flag


@grp2.command()
def cmd2(fraction: float):
    return {"verbosity": _verbosity, "flag": _flag, "fraction": fraction}


#  this works
app.add_typer(grp2, name="grp1")


@grp2.command()
def cmd1(count: int):
    return {"verbosity": _verbosity, "flag": _flag, "count": count}


def run_subgrp(msg: str):
    return {"verbosity": _verbosity, "flag": _flag, "msg": msg}


subgrp = Typer(name="subgrp", invoke_without_command=True, callback=run_subgrp)

grp2.add_typer(subgrp)
