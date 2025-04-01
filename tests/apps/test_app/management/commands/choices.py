import typing as t
import json
import typer
from django_typer.management import Typer
from django_typer.parsers.model import ModelObjectParser, ReturnType
from django_typer.completers import these_strings
from django.db.models import QuerySet

from tests.apps.test_app.models import ChoicesShellCompleteTester


app = Typer()


def model_parser(field: str) -> ModelObjectParser:
    return ModelObjectParser(
        ChoicesShellCompleteTester,
        field,
        return_type=ReturnType.QUERY_SET,
    )


@app.command()
def choices(
    char_choices: t.Annotated[
        QuerySet[ChoicesShellCompleteTester],
        typer.Option(
            parser=model_parser("char_choice"),
            shell_complete=these_strings(
                ChoicesShellCompleteTester.CHAR_CHOICES,
                allow_duplicates=False,
            ),
            help="Fetch objects by their char choice fields.",
        ),
    ] = ChoicesShellCompleteTester.objects.none(),
    int_choices: t.Annotated[
        QuerySet[ChoicesShellCompleteTester],
        typer.Option(
            parser=model_parser("int_choice"),
            shell_complete=these_strings(
                ChoicesShellCompleteTester.INT_CHOICES,
                allow_duplicates=False,
            ),
            help="Fetch objects by their int choice fields.",
        ),
    ] = ChoicesShellCompleteTester.objects.none(),
    ip_choices: t.Annotated[
        QuerySet[ChoicesShellCompleteTester],
        typer.Option(
            parser=model_parser("ip_choice"),
            shell_complete=these_strings(
                ChoicesShellCompleteTester.IP_CHOICES,
                allow_duplicates=False,
            ),
            help="Fetch objects by their ip choice fields.",
        ),
    ] = ChoicesShellCompleteTester.objects.none(),
):
    objects = {
        "char_choice": {},
        "int_choice": {},
        "ip_choice": {},
    }
    for choice_field, record in objects.items():
        for choice in locals()[f"{choice_field}"] or []:
            assert isinstance(choice, ChoicesShellCompleteTester)
            record.setdefault(getattr(choice, choice_field), [])
            record[getattr(choice, choice_field)].append(choice.pk)

    return json.dumps(objects)
