from . import native_groups_self
from django_typer import Typer, TyperCommand
from django_typer.types import Verbosity
from django.utils.translation import gettext_lazy as _

Command: TyperCommand

app = Typer(native_groups_self.app)


@app.initialize(invoke_without_command=True)
def init(self, verbosity: Verbosity = 0, fog: bool = False):
    self.verbosity = verbosity
    self.fog = fog
    return {"verbosity": verbosity, "fog": self.fog}


@app.init_grp1.initialize(name="grp1")
def init_grp1(self, flag: int = 4):
    """
    Override GRP1 (initialize only)
    """
    self.flag = flag


assert Command  # type: ignore
Command.suppressed_base_arguments = {
    "--force-color",
    "--traceback",
    "--skip-checks",
    "--pythonpath",
}
