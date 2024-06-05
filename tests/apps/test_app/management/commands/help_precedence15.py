import json

from django.utils.translation import gettext_lazy as _

from .help_precedence8 import Command as BaseCommand


# if you really want to use a class docstring to override a base class help at
# higher precedence you can unset the base class help attribute by setting the
# higher precedence values to empty strings
class Command(BaseCommand, help=_("")):
    """
    Now class docstring is used!
    """

    help = ""

    def handle(self, arg1: str, arg2: str, arg3: float = 0.5, arg4: int = 1):
        assert self.__class__ is Command
        opts = {"arg1": arg1, "arg2": arg2, "arg3": arg3, "arg4": arg4}
        return json.dumps(opts)
