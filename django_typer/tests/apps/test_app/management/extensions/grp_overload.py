from django_typer.tests.apps.test_app.management.commands.grp_overload import (
    Command as GrpOverload,
)


@GrpOverload.g0.l2.command()
def cmd2():
    return f"g0:l2:cmd2()"


@GrpOverload.g1.l2.command()
def cmd2(self):
    assert self.__class__ is GrpOverload
    return f"g1:l2:cmd2()"
