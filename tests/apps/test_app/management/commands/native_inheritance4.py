from django_typer.management import Typer

from . import native_groups_self

app = Typer(native_groups_self.app)
