from django_typer.tests.apps.test_app.management.commands.native_override_init import (
    Command as NativeOverrideInit,
)
from django_typer.types import Verbosity


@NativeOverrideInit.initialize()
def init(self, verbosity: Verbosity = 0, bog: bool = False):
    self.verbosity = verbosity
    self.bog = bog
    return {"verbosity": self.verbosity, "bog": self.bog}


@NativeOverrideInit.group()
def grp2(self):
    """
    test_app2::grp2
    """
    self.grp2_called = True


@grp2.command(name="cmd1")
def grp2_cmd1(self, g2arg1: int):
    """
    test_app2::grp2::grp2_cmd1
    """
    return {
        "verbosity": self.verbosity,
        "bog": self.bog,
        "grp2_called": getattr(self, "grp2_called", None),
        "g2arg1": g2arg1,
    }
