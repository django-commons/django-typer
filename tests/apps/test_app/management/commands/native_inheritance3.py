from django_typer import Typer

from . import native_groups

app = Typer(native_groups.app)
