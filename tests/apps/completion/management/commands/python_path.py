import typing as t
from django_typer.management import TyperCommand
from typer import Option


def complete(ctx, param, incomplete):
    from path_test import mod

    return [mod.option]


class Command(TyperCommand):
    def handle(
        self,
        option: t.Annotated[
            str,
            Option(
                help="An option that requires --pythonpath to be passed for tab completion to work.",
                shell_complete=complete,
            ),
        ],
    ):
        return option
