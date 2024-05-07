from django_typer import TyperCommand, initialize
from typer import Argument, Option
from django.conf import settings
import sys
import typing as t

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

COMMAND_TMPL = """
def {routine}(self, {flag_args}):
    flags = []
    {add_flags}
    return self.run("{routine}", flags)
"""


class Command(TyperCommand):
    @initialize()
    def init(self):
        pass

    def run(self, routine: str, flags: t.Optional[t.List[str]]):
        return routine, flags


for routine, flags in getattr(settings, "ROUTINES", {}).items():
    flag_args = ", ".join([f"{flag}: bool=False" for flag in flags])
    add_flags = ""
    for flag in flags:
        add_flags += f'\n    if {flag}: flags.append("{flag}")'
    exec(COMMAND_TMPL.format(routine=routine, flag_args=flag_args, add_flags=add_flags))
    Command.command()(locals()[routine])
