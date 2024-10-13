import sys
import typing as t

from django.conf import settings

from django_typer.management import TyperCommand, initialize


COMMAND_TMPL = """
def {routine}(self, {flag_args}):
    flags = []
    {add_flags}
    return self.run("{routine}", flags)
"""


class Command(TyperCommand):
    @initialize()
    def init(self):
        assert self.__class__ is Command

    def run(self, routine: str, flags: t.Optional[t.List[str]]):
        assert self.__class__ is Command
        return routine, flags


for routine, flags in getattr(settings, "ROUTINES", {}).items():
    flag_args = ", ".join([f"{flag}: bool=False" for flag in flags])
    add_flags = ""
    for flag in flags:
        add_flags += f'\n    if {flag}: flags.append("{flag}")'
    exec(COMMAND_TMPL.format(routine=routine, flag_args=flag_args, add_flags=add_flags))
    Command.command()(locals()[routine])
