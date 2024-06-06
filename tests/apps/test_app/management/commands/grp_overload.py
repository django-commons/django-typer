from django_typer.management import TyperCommand, group


class Command(TyperCommand):
    @group()
    def g0():
        pass

    @group()
    def g1(self):
        assert self.__class__ is Command

    @g0.group(invoke_without_command=True)
    def l2(self, arg: int):
        assert self.__class__ is Command
        return f"g0:l2({arg})"

    @g1.group(invoke_without_command=True)
    def l2(arg: str):
        return f"g1:l2({arg})"

    @g0.l2.command()
    def cmd():
        return "g0:l2:cmd()"

    @g1.l2.command()
    def cmd(self):
        assert self.__class__ is Command
        return "g1:l2:cmd()"
