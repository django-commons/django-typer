from tests.apps.test_app.management.commands.adapted2 import (
    Command as Adapted2,
)


@Adapted2.command()
def top1(self, msg1: str):
    """Extend with top level command."""
    assert self.__class__ is Adapted2
    return f"adapter1::adapted2({self.verbosity})::top1({msg1})"


@Adapted2.grp1.command()
def grp1_adpt1(self, int_arg1: int):
    """Extend grp1 with command."""
    assert self.__class__ is Adapted2
    return f"adapter1::adapted2({self.verbosity})::grp1({self.argg3})::grp1_adpt1({int_arg1})"


@Adapted2.group(invoke_without_command=True)
def grp3(self):
    assert self.__class__ is Adapted2
    return f"adapter1::adapted2({self.verbosity})::grp3()"


@Adapted2.grp2.group(invoke_without_command=True)
def sub_grp2(self, int_arg2: int):
    assert self.__class__ is Adapted2
    return f"adapter1::adapted2({self.verbosity})::grp2({self.flag1})::sub_grp2({int_arg2})"


@Adapted2.subsubgroup.command()
def ssg_cmd(self, int_arg3: int):
    assert self.__class__ is Adapted2
    return f"adapter1::interference::grp1({self.argg3})::subgroup({self.arg5_0})::subsubgroup({self.subsubgroup_called})::ssg_cmd({int_arg3})"
