from django_typer.management import TyperCommand, command, finalize
from click import get_current_context


class Command(TyperCommand, chain=True):
    @finalize()
    def final(self, result):
        assert isinstance(self, Command)
        return "finalized: {}".format(result)

    @command()
    def cmd1(self, arg1: int = 1):
        return "cmd1 {}".format(arg1)

    @command()
    def cmd2(self, arg2: int):
        return "cmd2 {}".format(arg2)
