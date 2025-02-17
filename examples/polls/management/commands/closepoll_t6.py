import typing as t

from django.utils.translation import gettext_lazy as _
from typer import Argument, Option

from django_typer.management import TyperCommand
from django_typer.utils import model_parser_completer
from tests.apps.examples.polls.models import Question as Poll


class Command(TyperCommand):
    help = _("Closes the specified poll for voting.")

    def handle(
        self,
        polls: t.Annotated[
            t.List[Poll],
            Argument(
                **model_parser_completer(Poll, help_field="question_text"),
                help=_("The database IDs of the poll(s) to close."),
            ),
        ],
        delete: t.Annotated[
            bool,
            Option(help=_("Delete poll instead of closing it.")),
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
