import typing as t

from django.core.management.base import CommandError
from django.utils.translation import gettext_lazy as _
from typer import Argument, Option

from django_typer import TyperCommand
from django_typer.tests.polls.models import Question as Poll


def get_poll_from_id(poll: t.Union[str, Poll]) -> Poll:
    if isinstance(poll, Poll):
        return poll
    try:
        return Poll.objects.get(pk=int(poll))
    except Poll.DoesNotExist:
        raise CommandError('Poll "%s" does not exist' % poll)


class Command(TyperCommand):
    help = "Closes the specified poll for voting"

    def handle(
        self,
        polls: t.Annotated[
            t.List[Poll],
            Argument(
                parser=get_poll_from_id,
                help=_("The database IDs of the poll(s) to close."),
            ),
        ],
        delete: t.Annotated[
            bool,
            Option(
                "--delete",  # we can also get rid of that unnecessary --no-delete flag
                help=_("Delete poll instead of closing it."),
            ),
        ] = False,
    ):
        for poll in polls:
            poll.opened = False
            poll.save()
            self.stdout.write(
                self.style.SUCCESS('Successfully closed poll "%s"' % poll.question_text)
            )
            if delete:
                poll.delete()
