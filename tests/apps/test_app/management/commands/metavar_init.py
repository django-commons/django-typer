"""
Test options metavar propagation and overrides
"""

from django_typer.management import TyperCommand, initialize


class Command(TyperCommand):
    @initialize()  # use default from TyperCommand
    def init(self):
        print("init")
