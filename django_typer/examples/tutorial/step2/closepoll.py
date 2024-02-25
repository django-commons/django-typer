import sys
import typing as t

if sys.version_info < (3, 9):
    from typing_extensions import Annotated
else:
    from typing import Annotated

from django.core.management.base import CommandError
from django.utils.translation import gettext_lazy as _
from typer import Argument, Option

from django_typer import TyperCommand
from django_typer.tests.polls.models import Question as Poll


class Command(TyperCommand):
    help = "Closes the specified poll for voting"

    def handle(
        self,
        poll_ids: Annotated[
            t.List[int], Argument(help=_("The database IDs of the poll(s) to close."))
        ],
        delete: Annotated[
            bool, Option(help=_("Delete poll instead of closing it."))
        ] = False,
    ):
        for poll_id in poll_ids:
            try:
                poll = Poll.objects.get(pk=poll_id)
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)

            poll.opened = False
            poll.save()

            self.stdout.write(
                self.style.SUCCESS('Successfully closed poll "%s"' % poll_id)
            )

            if delete:
                poll.delete()
