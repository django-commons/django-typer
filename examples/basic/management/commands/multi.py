import typing as t

from django.utils.translation import gettext_lazy as _
from typer import Argument

from django_typer.management import TyperCommand, command


class Command(TyperCommand):
    """
    A command that defines subcommands.
    """

    @command()
    def create(
        self,
        name: t.Annotated[
            str, Argument(help=_("The name of the object to create."))
        ],
    ):
        """
        Create an object.
        """

    @command()
    def delete(
        self,
        id: t.Annotated[
            int, Argument(help=_("The id of the object to delete."))
        ],
    ):
        """
        Delete an object.
        """
