from . import native_groups
from django.utils.translation import gettext_lazy as _


class Command(native_groups.Command):
    @native_groups.Command.init_grp1.group(name="subgrp")
    def run_subgrp(self, option1: bool = False, option2: bool = False):
        """
        Override SUBGROUP
        """
        self.option1 = option1
        self.option2 = option2

    @run_subgrp.command()
    def sg_cmd1(self):
        """
        Subgroup command 1. No args.
        """
        return {
            "verbosity": native_groups._verbosity,
            "flag": native_groups._flag,
            "option1": self.option1,
            "option2": self.option2,
        }

    @run_subgrp.command(help=_("Subgroup command 2, Takes an int."))
    def sg_cmd2(self, number: int):
        return {
            "verbosity": native_groups._verbosity,
            "flag": native_groups._flag,
            "option1": self.option1,
            "option2": self.option2,
            "number": number,
        }
