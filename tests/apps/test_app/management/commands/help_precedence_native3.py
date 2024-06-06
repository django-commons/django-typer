from django.utils.translation import gettext_lazy as _

from django_typer.management import Typer


app = Typer()


@app.command()
def native_helps():
    """
    3: Docstring help
    """
