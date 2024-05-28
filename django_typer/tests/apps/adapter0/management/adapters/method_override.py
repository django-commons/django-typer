from django_typer.tests.apps.test_app.management.commands.method_override import (
    Command as MethodOverride,
)


@MethodOverride.initialize(invoke_without_command=True)
def init(self):
    """
    Command1
    """
    assert self.__class__ is MethodOverride
    return f"adapter0::init()"


@MethodOverride.command()
def cmd1(self):
    """
    Command1
    """
    assert self.__class__ is MethodOverride
    return f"adapter0::cmd1()"


@MethodOverride.command()
def cmd2(self):
    """
    Command1
    """
    assert self.__class__ is MethodOverride
    return f"adapter0::cmd2()"
