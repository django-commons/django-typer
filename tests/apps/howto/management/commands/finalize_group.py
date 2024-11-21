import typing as t
from django_typer.management import TyperCommand, command, finalize, group


class Command(TyperCommand, chain=True):
    """
    Show that finalizers are hierarchical and results are collected and
    passed to the finalizer of the parent group if one exists.
    """

    @finalize()
    def to_csv(self, results: t.List[str]):
        return ", ".join(results)

    @command()
    def cmd1(self):
        return "result1"

    @command()
    def cmd2(self):
        return "result2"

    @group(chain=True)
    def grp(self):
        return "grp"

    @grp.finalize()
    def to_upper_csv(self, results):
        return ", ".join([result.upper() for result in results])

    @grp.command()
    def cmd3(self):
        return "result3"

    @grp.command()
    def cmd4(self):
        return "result4"
