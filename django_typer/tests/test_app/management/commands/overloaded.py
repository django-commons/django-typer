import json
import typing as t

from django.utils.translation import gettext_lazy as _
from typer import Argument, Option

from django_typer import TyperCommand, group


class Command(TyperCommand):
    help = _("Test overloaded option and argument names")

    parameters = {}

    @group()
    def test(
        self, precision: int, flag: t.Annotated[bool, Option(help="A flag.")] = False
    ):
        """
        Do some math at the given precision.
        """
        self.parameters = {}
        self.parameters["test"] = {
            "precision": precision,
            "flag": flag,
        }

    @test.command()
    def samename(
        self, precision: int, flag: t.Annotated[bool, Option(help="A flag.")] = False
    ):
        self.parameters["samename"] = {
            "precision": precision,
            "flag": flag,
        }
        return json.dumps(self.parameters, indent=2)

    @test.command()
    def diffname(
        self,
        precision2: t.Annotated[int, Argument(metavar="precision")],
        flag2: t.Annotated[bool, Option("--flag/--no-flag", help="A flag.")] = False,
    ):
        self.parameters["diffname"] = {
            "precision2": precision2,
            "flag2": flag2,
        }
        return json.dumps(self.parameters, indent=2)
