from django_typer.management import TyperCommand, command, group, initialize


class Command(TyperCommand):
    help = "Test that inheritence extensions do not interfere with base classes."

    arg5_0: bool
    subsubgroup_called: bool = False

    @initialize(invoke_without_command=True)
    def init(self, arg: bool = True):
        assert isinstance(self, Command)
        return f"test_app::interference::init({arg})"

    @command()
    def cmd1(self, arg1_0: str):
        """
        Command 1, takes an str.
        """
        assert isinstance(self, Command)
        return f"test_app::interference::cmd1({arg1_0})"

    @command()
    def cmd2(self, arg2_0: int):
        """
        Command 2, takes an int.
        """
        assert isinstance(self, Command)
        return f"test_app::interference::cmd2({arg2_0})"

    @group(invoke_without_command=True)
    def grp1(self, argg3: float):
        """
        Group 1, take a float.
        """
        assert isinstance(self, Command)
        self.argg3 = argg3
        return f"test_app::interference::grp1({argg3})"

    @grp1.command()
    def cmd3(self, arg3_0: str, arg3_1: str):
        """
        Command 3, take two strings.
        """
        assert isinstance(self, Command)
        return f"test_app::interference::grp1({self.argg3})::cmd3({arg3_0}, {arg3_1})"

    @grp1.command()
    def cmd4(self, arg4_0: int, arg4_1: int):
        """
        Command 4, take two ints.
        """
        assert isinstance(self, Command)
        return f"test_app::interference::grp1({self.argg3})::cmd4({arg4_0}, {arg4_1})"

    @grp1.group(invoke_without_command=True)
    def subgroup(self, arg5_0: bool = False):
        assert isinstance(self, Command)
        self.arg5_0 = arg5_0
        return f"test_app::interference::grp1({self.argg3})::subgroup({arg5_0})"

    @subgroup.command()
    def subcommand(self):
        assert isinstance(self, Command)
        return f"test_app::interference::grp1({self.argg3})::subgroup({self.arg5_0})::subcommand()"

    @subgroup.group()
    def subsubgroup(self):
        assert isinstance(self, Command)
        self.subsubgroup_called = True

    @subsubgroup.command()
    def subsubcommand(self):
        assert isinstance(self, Command)
        return f"test_app::interference::grp1({self.argg3})::subgroup({self.arg5_0})::subsubgroup({self.subsubgroup_called})::subsubcommand()"
