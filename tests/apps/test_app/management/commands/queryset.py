from typing import Annotated

import typer
import json

from django_typer.management import TyperCommand
from django_typer.parsers.model import ReturnType
from django_typer.utils import duration_iso_string, model_parser_completer
from tests.apps.test_app.models import ShellCompleteTester
from django.db.models import QuerySet


class Command(TyperCommand, rich_markup_mode="rich"):
    def handle(
        self,
        query: Annotated[
            QuerySet[ShellCompleteTester],
            typer.Argument(
                **model_parser_completer(
                    ShellCompleteTester,
                    lookup_field="duration_field",
                    return_type=ReturnType.QUERY_SET,
                )
            ),
        ],
    ):
        assert self.__class__ is Command
        assert isinstance(query, QuerySet)
        return json.dumps(
            {obj.id: duration_iso_string(obj.duration_field) for obj in query}
        )
