from django_typer.management import group, initialize
from django_typer import types

from .interference import Command as Interference

from typing import Annotated

import typer


class Command(Interference):
    verbosity = 1

    flag1: bool

    @initialize()
    def init(
        self,
        verbosity: Annotated[
            int,
            typer.Option(
                help=(
                    "Verbosity level; 0=minimal output, 1=normal output, "
                    "2=verbose output, 3=very verbose output"
                ),
                show_choices=True,
                min=0,
                max=5,
                rich_help_panel=types.COMMON_PANEL,
            ),
        ] = verbosity,
    ):
        assert isinstance(self, Command)
        self.verbosity = verbosity

    @group()
    def grp2(self, flag1: bool = False):
        """Group 2, take a flag"""
        assert isinstance(self, Command)
        self.flag1 = flag1

    @grp2.command()
    def grp2_cmd1(self, cmd1_arg: str):
        assert isinstance(self, Command)
        return f"test_app::adapted2({self.verbosity})::grp2({self.flag1})::grp2_cmd1({cmd1_arg})"

    @grp2.command()
    def grp2_cmd2(self, cmd2_arg: str):
        assert isinstance(self, Command)
        return f"test_app::adapted2({self.verbosity})::grp2({self.flag1})::grp2_cmd2({cmd2_arg})"

    @Interference.grp1.command()
    def grp1_ext(self):
        """Inherit/extend grp1 with a cmd"""
        assert isinstance(self, Command)
        return f"test_app::adapted2({self.verbosity})::grp1({self.argg3})::grp1_ext()"
