from tests.apps.test_app.management.commands.grp_overload import (
    Command as GrpOverload,
)


# print(f'g0={hex(id(GrpOverload.g0))}, g0.l2={hex(id(GrpOverload.g0.l2))}')
@GrpOverload.g0.l2.command()
def cmd2():
    return "g0:l2:cmd2()"


# print(f'g1={hex(id(GrpOverload.g1))}, g1.l2={hex(id(GrpOverload.g1.l2))}')
@GrpOverload.g1.l2.command()
def cmd2(self):
    assert self.__class__ is GrpOverload
    return "g1:l2:cmd2()"


@GrpOverload.group(invoke_without_command=True)
def g2(self):
    return "g2()"


@g2.group()
def l2():
    return "g2:l2()"
