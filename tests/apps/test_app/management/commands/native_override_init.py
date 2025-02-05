import typing as t
from django_typer.management import Typer, TyperCommand
from django_typer.types import Verbosity

from . import native_groups_self

Command: t.Type[TyperCommand]

app = Typer(native_groups_self.app)


@app.initialize(invoke_without_command=True)
def init(self, verbosity: Verbosity = 0, fog: bool = False):
    assert native_groups_self.app.django_command
    assert not isinstance(self, native_groups_self.app.django_command)
    assert app.django_command
    assert isinstance(self, app.django_command)
    self.verbosity = verbosity
    self.fog = fog
    return {"verbosity": verbosity, "fog": self.fog}


@app.init_grp1.initialize()  # name="grp1")
def init_grp1(self, flag: int = 4):
    """
    Override GRP1 (initialize only)
    """
    assert not isinstance(self, native_groups_self.Command)
    assert isinstance(self, Command)
    self.flag = flag


assert Command  # type: ignore
Command.suppressed_base_arguments = {
    "--force-color",
    "--traceback",
    "--skip-checks",
    "--pythonpath",
    "--show-locals",
    "--hide-locals",
}
