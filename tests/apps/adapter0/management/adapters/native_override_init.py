from tests.apps.test_app.management.commands.native_override_init import (
    Command,
    app,
)
from django_typer.types import Verbosity


@app.initialize()
def init(self, verbosity: Verbosity = 0, bog: bool = False):
    self.verbosity = verbosity
    self.bog = bog
    assert self.__class__ is Command
    return {"verbosity": self.verbosity, "bog": self.bog}


@app.group()
def grp2(self):
    """
    test_app2::grp2
    """
    assert self.__class__ is Command
    self.grp2_called = True


@app.grp2.command(name="cmd1")
def grp2_cmd1(self, g2arg1: int):
    """
    test_app2::grp2::grp2_cmd1
    """
    assert self.__class__ is Command
    return {
        "verbosity": self.verbosity,
        "bog": self.bog,
        "grp2_called": getattr(self, "grp2_called", None),
        "g2arg1": g2arg1,
    }
