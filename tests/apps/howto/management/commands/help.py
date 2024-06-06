from django.utils.translation import gettext_lazy as _

from django_typer.management import TyperCommand, command


class Command(TyperCommand, help=_("2")):
    """
    5: Command class docstrings are the last resort for
    the upper level command help string.
    """

    help = _("3")

    # if an initializer is present it's help will be used for the command
    # level help

    @command(help=_("1"))
    def handle(self):
        """
        4: Function docstring is last priority and is not subject to
           translation.
        """
