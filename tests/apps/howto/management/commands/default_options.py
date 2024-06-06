from django_typer.management import TyperCommand
from django_typer.types import Verbosity


class Command(TyperCommand):
    suppressed_base_arguments = ["--settings"]  # remove the --settings option

    def handle(self, verbosity: Verbosity = 1): ...
