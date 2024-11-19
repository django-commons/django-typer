from django_typer.management import TyperCommand, command, finalize
from click import get_current_context


class Command(TyperCommand, chain=True):
    @finalize()
    def final(self, result):
        assert isinstance(self, Command)
        return "finalized: {}".format(result)

    @command()
    def cmd1(self):
        return "cmd1"

    @command()
    def cmd2(self):
        return "cmd2"
