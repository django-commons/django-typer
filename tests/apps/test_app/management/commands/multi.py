import json
from typing import List

from django_typer.management import TyperCommand, command


class Command(TyperCommand):
    help = "Test multiple sub-commands."

    @command()
    def cmd1(self, files: List[str], flag1: bool = False):
        """
        A command that takes a list of files and a flag.
        """
        assert self.__class__ is Command
        return json.dumps({"files": files, "flag1": flag1})

    @command()
    def sum(self, numbers: List[float]):
        """
        Sum the given numbers.
        """
        assert self.__class__ is Command
        return str(sum(numbers))

    @command()
    def cmd3(self):
        """
        A command with no arguments.
        """
        assert self.__class__ is Command
        return json.dumps({})
