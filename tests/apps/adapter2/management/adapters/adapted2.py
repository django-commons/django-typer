from tests.apps.test_app.management.commands.adapted2 import (
    Command as Adapted2,
)


@Adapted2.command()
def top1(self):
    """Extend with top level command."""
    assert self.__class__ is Adapted2
    return f"adapter2::adapted2({self.verbosity})::top1()"


@Adapted2.grp1.command()
def grp1_adpt1(self, int_arg1: int, int_arg1_2: int):
    """Extend grp1 with command."""
    assert self.__class__ is Adapted2
    return f"adapter2::adapted2({self.verbosity})::grp1({self.argg3})::grp1_adpt1({int_arg1}, {int_arg1_2})"


@Adapted2.grp2.group(invoke_without_command=True)
def sub_grp2(self, int_arg2: int, int_arg2_2: int):
    assert self.__class__ is Adapted2
    return f"adapter2::adapted2({self.verbosity})::grp2({self.flag1})::sub_grp2({int_arg2}, {int_arg2_2})"


try:

    @sub_grp2.group(invoke_without_command=True)
    def subsub_grp2():
        return "adapter2::adapted2()::grp2()::sub_grp2()::subsub_grp2()"

    assert False, (
        "Should not be able to do this, because we must always be very specific as to which command we are modifying"
    )
except AssertionError:
    pass


@Adapted2.sub_grp2.group(invoke_without_command=True)
def subsub_grp2():
    return "adapter2::adapted2()::grp2()::sub_grp2()::subsub_grp2()"


@Adapted2.subsubgroup.command()
def ssg_cmd(self, int_arg3: int, int_arg3_2: int):
    assert self.__class__ is Adapted2
    return f"adapter2::interference::grp1({self.argg3})::subgroup({self.arg5_0})::subsubgroup({self.subsubgroup_called})::ssg_cmd({int_arg3}, {int_arg3_2})"
