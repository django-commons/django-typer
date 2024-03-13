import sys
import typing as t

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

from typer import Option

from django_typer import TyperCommand, model_parser_completer
from django_typer.tests.polls.models import Question as Poll


class Command(TyperCommand):
    help = "Closes the specified poll for voting"

    def handle(
        self,
        polls: Annotated[
            t.List[Poll],
            Option(**model_parser_completer(Poll, help_field="question_text")),
        ],
        delete: Annotated[
            bool, Option(help="Delete poll instead of closing it.")
        ] = False,
    ):
        for poll in polls:
            poll.opened = False
            poll.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully closed poll "{poll.id}"')
            )
            if delete:
                poll.delete()
