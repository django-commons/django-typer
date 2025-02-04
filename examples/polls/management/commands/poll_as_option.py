import typing as t

from typer import Option

from django_typer.management import TyperCommand
from django_typer.utils import model_parser_completer
from tests.apps.examples.polls.models import Question as Poll


class Command(TyperCommand):
    help = "Closes the specified poll for voting"

    def handle(
        self,
        polls: t.Annotated[
            t.List[Poll],
            Option(
                **model_parser_completer(Poll, help_field="question_text"),
                metavar="POLL",
            ),
        ],
        delete: t.Annotated[
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
