import typing as t

from typer import Argument, Option

from django_typer import TyperCommand, completers, parsers
from django_typer.tests.polls.models import Question as Poll


class Command(TyperCommand):
    help = "Closes the specified poll for voting"

    def handle(
        self,
        polls: t.Annotated[
            t.List[Poll],
            Argument(
                parser=parsers.ModelObjectParser(Poll),
                shell_complete=completers.ModelObjectCompleter(
                    Poll, help_field="question_text"
                ),
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
                self.style.SUCCESS(f'Successfully closed poll "{{ poll.id }}"')
            )
            if delete:
                poll.delete()
