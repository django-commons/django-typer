from django_typer.management import Typer

from . import native

app = Typer(native.app)
