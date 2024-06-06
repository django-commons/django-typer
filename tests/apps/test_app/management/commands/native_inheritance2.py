from django_typer.management import Typer

from . import native_self

app = Typer(native_self.app)
