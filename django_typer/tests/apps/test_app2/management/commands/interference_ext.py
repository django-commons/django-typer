from django_typer import initialize, command, group
from django_typer.tests.apps.test_app.management.commands.interference import (
    Command as Interference,
)


class Command(Interference):
    help = "Inherited and extend interference"

    @initialize(invoke_without_command=True)
    def init(self, arg: bool = True):
        return f"test_app2::interference::init({arg})"

    @command()
    def cmd1(self, arg1: int):
        """
        Command 1, takes an int.
        """
        return f"test_app2::interference::cmd1({arg1})"

    @command()
    def cmd_ext(self):
        """
        Command EXT.
        """
        return f"test_app2::interference::cmd_ext()"

    @Interference.command()
    def adapt_cmd(self):
        """Should be equivalent to @command()"""
        return f"test_app2::interference::adapt_cmd()"

    @Interference.group(invoke_without_command=True)
    def adapt_group(self):
        """Should be equivalent to @group()"""
        return f"test_app2::interference::adapt_group()"

    @group(invoke_without_command=True)
    def grp2(self, argg2: str):
        """
        Group 2, take a str.
        """
        return f"test_app2::interference::grp2({argg2})"

    @Interference.grp1.command()
    def cmd3(self, arg3_0: int, arg3_1: int):
        """
        Command 3, take two ints.
        """
        return f"test_app2::interference::grp1({self.argg3})::cmd3({arg3_0}, {arg3_1})"

    @Interference.subgroup.command()
    def cmd5(self):
        return f"test_app2::interference::grp1({self.argg3})::subgroup({self.arg5_0})::cmd5()"

    @Interference.subsubgroup.command()
    def subsubcommand(self):
        return f"test_app2::interference::grp1({self.argg3})::subgroup({self.arg5_0})::subsubgroup({self.subsubgroup_called})::subsubcommand()"

    @Interference.subsubgroup.command()
    def subsubcommand2(self):
        return f"test_app2::interference::grp1({self.argg3})::subgroup({self.arg5_0})::subsubgroup({self.subsubgroup_called})::subsubcommand2()"
