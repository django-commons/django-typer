import json
import sys
from typing import Annotated

from django.utils.translation import gettext_lazy as _
from typer import Argument, Option

from django_typer.management import TyperCommand, group


class Command(TyperCommand):
    help = _("Test overloaded option and argument names")

    parameters = {}

    @group()
    def test(
        self, precision: int, flag: Annotated[bool, Option(help="A flag.")] = False
    ):
        """
        Do some math at the given precision.
        """
        assert self.__class__ is Command
        self.parameters = {}
        self.parameters["test"] = {
            "precision": precision,
            "flag": flag,
        }

    @test.command()
    def samename(
        self, precision: int, flag: Annotated[bool, Option(help="A flag.")] = False
    ):
        assert self.__class__ is Command
        self.parameters["samename"] = {
            "precision": precision,
            "flag": flag,
        }
        return json.dumps(self.parameters, indent=2)

    @test.command()
    def diffname(
        self,
        precision2: Annotated[int, Argument(metavar="precision")],
        flag2: Annotated[bool, Option("--flag/--no-flag", help="A flag.")] = False,
    ):
        assert self.__class__ is Command
        self.parameters["diffname"] = {
            "precision2": precision2,
            "flag2": flag2,
        }
        return json.dumps(self.parameters, indent=2)
