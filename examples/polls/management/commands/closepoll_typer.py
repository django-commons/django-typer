import typing as t

from typer import Argument, Option

from django_typer.management import Typer
from django_typer.utils import model_parser_completer
from tests.apps.examples.polls.models import Question as Poll

app = Typer(help="Closes the specified poll for voting")


@app.command()
def handle(
    self,
    polls: t.Annotated[
        t.List[Poll],
        Argument(**model_parser_completer(Poll, help_field="question_text")),
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
