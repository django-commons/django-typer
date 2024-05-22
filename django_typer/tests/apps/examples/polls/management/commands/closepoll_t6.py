import sys
import typing as t

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

from django.utils.translation import gettext_lazy as _
from typer import Argument, Option

from django_typer import TyperCommand, model_parser_completer
from django_typer.tests.apps.examples.polls.models import Question as Poll


class Command(TyperCommand):
    help = _("Closes the specified poll for voting.")

    def handle(
        self,
        polls: Annotated[
            t.List[Poll],
            Argument(
                **model_parser_completer(Poll, help_field="question_text"),
                help=_("The database IDs of the poll(s) to close."),
            ),
        ],
        delete: Annotated[
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
