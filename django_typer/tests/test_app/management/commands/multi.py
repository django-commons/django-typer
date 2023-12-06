from django_typer import TyperCommand, command
from typing import List
import json


class Command(TyperCommand):
    
    help = 'Test multiple sub-commands.'

    @command()
    def cmd1(files: List[str], flag1: bool = False):
        """
        A command that takes a list of files and a flag.
        """
        return json.dumps({
            'files': files,
            'flag1': flag1
        })
    
    @command()
    def sum(numbers: List[float]):
        """
        Sum the given numbers.
        """
        return sum(numbers)

    @command()
    def cmd3():
        """
        A command with no arguments.
        """
        return json.dumps({})
