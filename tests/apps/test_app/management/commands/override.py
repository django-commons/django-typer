from django_typer.management import TyperCommand

import typing as t
from enum import Enum
from pathlib import Path

from typer import Argument, Option


class VersionEnum(str, Enum):
    VERSION1 = "1"
    VERSION1_1 = "1.1"
    VERSION2 = "2"


class Command(TyperCommand):
    help = "Override some default django options."

    def handle(
        self,
        settings: t.Annotated[
            Path, Argument(help="Override default settings argument.")
        ],
        optional_arg: t.Annotated[int, Argument(help="An optional argument.")] = 0,
        version: t.Annotated[
            t.Optional[VersionEnum],
            Option("--version", help="Override default version argument."),
        ] = None,
    ):
        assert self.__class__ is Command
        return {
            "settings": settings,
            "version": version,
            **({"optional_arg": optional_arg} if optional_arg else {}),
        }
