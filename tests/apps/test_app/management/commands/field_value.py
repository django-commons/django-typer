from typing import Annotated

import typer
from django.utils.translation import gettext_lazy as _
from datetime import timedelta
from django.core.management.base import CommandError

from django_typer.management import TyperCommand
from django_typer.parsers.model import ReturnType
from tests.apps.test_app.models import ShellCompleteTester
from django_typer.utils import duration_iso_string, model_parser_completer


def test_custom_error_message(model_cls, field_value: str, exception: Exception):
    raise CommandError(
        f"Test custom error message: {model_cls=}, {field_value=}, {exception=}"
    )


class Command(TyperCommand, rich_markup_mode="rich"):
    def handle(
        self,
        duration: Annotated[
            timedelta,
            typer.Argument(
                **model_parser_completer(
                    ShellCompleteTester,
                    lookup_field="duration_field",
                    return_type=ReturnType.FIELD_VALUE,
                    on_error=test_custom_error_message,
                )
            ),
        ],
    ):
        assert self.__class__ is Command
        assert isinstance(duration, timedelta)
        return duration_iso_string(duration)
