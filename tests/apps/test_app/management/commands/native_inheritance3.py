from django_typer.management import Typer

from . import native_groups

app = Typer(native_groups.app)
