from typing import Annotated

import typer
from django.utils.translation import gettext_lazy as _
from datetime import timedelta

from django_typer.management import TyperCommand, model_parser_completer
from django_typer.parsers.model import ReturnType
from tests.apps.test_app.models import ShellCompleteTester
from django_typer.utils import duration_iso_string


class Command(TyperCommand, rich_markup_mode="rich"):
    def handle(
        self,
        duration: Annotated[
            timedelta,
            typer.Argument(
                **model_parser_completer(
                    ShellCompleteTester, return_type=ReturnType.FIELD_VALUE
                )
            ),
        ],
    ):
        assert self.__class__ is Command
        assert isinstance(duration, timedelta)
        return duration_iso_string(duration)
