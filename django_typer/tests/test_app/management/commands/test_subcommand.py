import json

from django_typer import TyperCommand, subcommand


class Command(TyperCommand):
    @subcommand
    def subcommand1(self, name: str, formal: bool = False):
        """This is a subcommand"""
        json.dumps({"name": name, "formal": formal})
