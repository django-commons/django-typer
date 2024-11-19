from django_typer.management import TyperCommand, command
from typing import List


def finalize(self: List["Command"], **_):
    assert isinstance(self[0], Command)
    return "finalize".format(self)


class Command(TyperCommand, result_callback=finalize, chain=True):
    @command()
    def cmd1(self):
        return self

    @command()
    def cmd2(self):
        return self
