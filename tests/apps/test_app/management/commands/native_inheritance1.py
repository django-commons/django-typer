from django_typer import Typer

from . import native

app = Typer(native.app)
