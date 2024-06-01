from django_typer import Typer
from django.utils.translation import gettext_lazy as _

# typer style commands use the Typer help precedence
app = Typer(help=_("2"))


@app.command(help=_("1"))
def handle(self):
    """
    3: Function docstring is last priority and is not subject to translation.
    """
