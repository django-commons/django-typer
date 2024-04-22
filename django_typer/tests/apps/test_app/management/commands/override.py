import sys

from django_typer import TyperCommand

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

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
        settings: Annotated[Path, Argument(help="Override default settings argument.")],
        optional_arg: Annotated[int, Argument(help="An optional argument.")] = 0,
        version: Annotated[
            t.Optional[VersionEnum],
            Option("--version", help="Override default version argument."),
        ] = None,
    ):
        return {
            "settings": settings,
            "version": version,
            **({"optional_arg": optional_arg} if optional_arg else {}),
        }
