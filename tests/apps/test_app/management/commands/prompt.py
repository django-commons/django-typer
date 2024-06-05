import sys
import typing as t

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

from django.utils.translation import gettext_lazy as _
from typer import Option

from django_typer import TyperCommand, command, group


class Command(TyperCommand):
    help = _("Test password prompt")

    @command()
    def cmd1(
        self,
        username: str,
        password: Annotated[
            t.Optional[str], Option("-p", hide_input=True, prompt=True)
        ] = None,
    ):
        assert self.__class__ is Command
        return f"{username} {password}"

    @command()
    def cmd2(
        self,
        username: str,
        password: Annotated[
            t.Optional[str],
            Option("-p", hide_input=True, prompt=True, prompt_required=False),
        ] = None,
    ):
        assert self.__class__ is Command
        return f"{username} {password}"

    @command()
    def cmd3(
        self,
        username: str,
        password: Annotated[
            str, Option("-p", hide_input=True, prompt=True, prompt_required=False)
        ] = "default",
    ):
        assert self.__class__ is Command
        return f"{username} {password}"

    @group()
    def group1(
        self,
        flag: Annotated[
            str, Option("-f", hide_input=True, prompt=True, prompt_required=True)
        ],
    ):
        assert self.__class__ is Command
        self.flag = flag

    @group1.command()
    def cmd4(
        self,
        username: str,
        password: Annotated[str, Option("-p", hide_input=True, prompt=True)],
    ):
        assert self.__class__ is Command
        return f"{self.flag} {username} {password}"
