"""
Test options metavar propagation and overrides
"""

from django_typer.management import TyperCommand, initialize


class Command(TyperCommand):
    @initialize(options_metavar="{INIT OPTS}")  # <-- override
    def init(self):
        print("init")
