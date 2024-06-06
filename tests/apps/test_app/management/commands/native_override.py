from django.utils.translation import gettext_lazy as _

from django_typer.management import Typer, TyperCommand

from . import native_groups

Command: TyperCommand

app = Typer(native_groups.app)


@app.init_grp1.group(name="subgrp")
def run_subgrp(self, option1: bool = False, option2: bool = False):
    """
    Override SUBGROUP
    """
    assert not isinstance(self, native_groups.Command)
    assert isinstance(self, Command)
    self.option1 = option1
    self.option2 = option2


@run_subgrp.command()
def sg_cmd1(self):
    """
    Subgroup command 1. No args.
    """
    assert not isinstance(self, native_groups.Command)
    assert isinstance(self, Command)
    return {
        "verbosity": native_groups._verbosity,
        "flag": native_groups._flag,
        "option1": self.option1,
        "option2": self.option2,
    }


@run_subgrp.command(help=_("Subgroup command 2, Takes an int."))
def sg_cmd2(self, number: int):
    assert not isinstance(self, native_groups.Command)
    assert isinstance(self, Command)
    return {
        "verbosity": native_groups._verbosity,
        "flag": native_groups._flag,
        "option1": self.option1,
        "option2": self.option2,
        "number": number,
    }
