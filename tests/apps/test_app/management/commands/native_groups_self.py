from django_typer.management import Typer, TyperCommand
from django_typer.types import Verbosity

app = Typer()


@app.callback()
def init(self, verbosity: Verbosity = 0):
    assert isinstance(self, TyperCommand)
    self.verbosity = verbosity


@app.command()
def main(self, name: str):
    assert isinstance(self, TyperCommand)
    return {"verbosity": self.verbosity, "name": name}


grp2 = Typer()


@grp2.callback()
def init_grp1(self, flag: bool = False):
    assert isinstance(self, TyperCommand)
    self.flag = flag


@grp2.command()
def cmd2(self, fraction: float):
    assert isinstance(self, TyperCommand)
    return {"verbosity": self.verbosity, "flag": self.flag, "fraction": fraction}


app.add_typer(grp2, name="grp1")


@grp2.command()
def cmd1(self, count: int):
    assert isinstance(self, TyperCommand)
    return {"verbosity": self.verbosity, "flag": self.flag, "count": count}


def run_subgrp(self, msg: str):
    assert isinstance(self, TyperCommand)
    return {"verbosity": self.verbosity, "flag": self.flag, "msg": msg}


subgrp = Typer(name="subgrp", invoke_without_command=True, callback=run_subgrp)

grp2.add_typer(subgrp)
