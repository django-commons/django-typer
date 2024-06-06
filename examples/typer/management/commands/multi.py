import typing as t

from django.utils.translation import gettext_lazy as _
from typer import Argument

from django_typer.management import Typer

app = Typer(help="A command that defines subcommands.")


@app.command()
def create(
    name: t.Annotated[
        str, Argument(help=_("The name of the object to create."))
    ],
):
    """
    Create an object.
    """


@app.command()
def delete(
    id: t.Annotated[int, Argument(help=_("The id of the object to delete."))],
):
    """
    Delete an object.
    """
