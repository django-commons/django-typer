"""
Test options metavar propagation and overrides
"""

from django_typer.management import initialize
from .metavar2 import Command as Metavar2Command


class Command(Metavar2Command):
    @initialize()  # should inherit from Metavar2Command class metavar
    def init(self):
        print("init")
