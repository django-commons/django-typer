import typing as t
from django_typer.management import TyperCommand, command, finalize


# chain=True allows multiple subroutines to be called from the command line
class Command(TyperCommand, chain=True):
    @finalize()
    def to_csv(self, results: t.List[str]):
        return ", ".join(results)

    @command()
    def cmd1(self):
        return "result1"

    @command()
    def cmd2(self):
        return "result2"
