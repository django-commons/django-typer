from django.utils.translation import gettext_lazy as _

from django_typer.management import Typer


app = Typer(help=_("2: App help"))


@app.command(help=_("1: Command help"))
def native_helps():
    """
    3: Docstring help
    """
