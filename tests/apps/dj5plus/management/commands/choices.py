import typing as t
import json
import typer
from django_typer.management import Typer
from django_typer.parsers.model import ModelObjectParser, ReturnType
from django_typer.completers import these_strings
from django.db.models.query import QuerySet

from tests.apps.dj5plus.models import ChoicesShellCompleteTesterDJ5Plus, get_ip_choices


app = Typer()


def model_parser(field: str) -> ModelObjectParser:
    return ModelObjectParser(
        ChoicesShellCompleteTesterDJ5Plus,
        field,
        return_type=ReturnType.QUERY_SET,
    )


@app.command()
def choices(
    char_choices: t.Annotated[
        QuerySet[ChoicesShellCompleteTesterDJ5Plus],
        typer.Option(
            parser=model_parser("char_choice"),
            shell_complete=these_strings(
                ChoicesShellCompleteTesterDJ5Plus.CHAR_CHOICES,
                allow_duplicates=False,
            ),
            help="Fetch objects by their char choice fields.",
        ),
    ] = ChoicesShellCompleteTesterDJ5Plus.objects.none(),
    int_choices: t.Annotated[
        QuerySet[ChoicesShellCompleteTesterDJ5Plus],
        typer.Option(
            parser=model_parser("int_choice"),
            shell_complete=these_strings(
                ChoicesShellCompleteTesterDJ5Plus.INT_CHOICES.items(),
                allow_duplicates=False,
            ),
            help="Fetch objects by their int choice fields.",
        ),
    ] = ChoicesShellCompleteTesterDJ5Plus.objects.none(),
    ip_choices: t.Annotated[
        QuerySet[ChoicesShellCompleteTesterDJ5Plus],
        typer.Option(
            parser=model_parser("ip_choice"),
            shell_complete=these_strings(get_ip_choices, allow_duplicates=False),
            help="Fetch objects by their ip choice fields.",
        ),
    ] = ChoicesShellCompleteTesterDJ5Plus.objects.none(),
):
    objects = {
        "char_choice": {},
        "int_choice": {},
        "ip_choice": {},
    }
    for choice_field, record in objects.items():
        for choice in locals()[f"{choice_field}s"] or []:
            assert isinstance(choice, ChoicesShellCompleteTesterDJ5Plus)
            record.setdefault(getattr(choice, choice_field), [])
            record[getattr(choice, choice_field)].append(choice.pk)

    return json.dumps(objects)
