from . import native_groups
from django_typer import Typer


app = Typer(native_groups.app)
