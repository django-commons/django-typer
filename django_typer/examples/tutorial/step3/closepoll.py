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
from django_typer.tests.apps.polls.models import Question as Poll


def get_poll_from_id(poll: t.Union[str, Poll]) -> Poll:
    if isinstance(poll, Poll):
        return poll
    try:
        return Poll.objects.get(pk=int(poll))
    except Poll.DoesNotExist:
        raise CommandError(f'Poll "{poll}" does not exist')


class Command(TyperCommand):
    def handle(
        self,
        polls: Annotated[
            t.List[Poll],
            Argument(
                parser=get_poll_from_id,
                help=_("The database IDs of the poll(s) to close."),
            ),
        ],
        delete: Annotated[
            bool,
            Option(
                "--delete",  # we can also get rid of that unnecessary --no-delete flag
                help=_("Delete poll instead of closing it."),
            ),
        ] = False,
    ):
        """
        Closes the specified poll for voting.


        As mentioned in the last section, helps can also
        be set in the docstring
        """
        for poll in polls:
            poll.opened = False
            poll.save()
            self.stdout.write(
                self.style.SUCCESS(f'Successfully closed poll "{poll.id}"')
            )
            if delete:
                poll.delete()
