import typing as t

from django.core.management.base import CommandError

from django_typer import TyperCommand
from django_typer.tests.polls.models import Question as Poll


class Command(TyperCommand):
    help = "Closes the specified poll for voting"

    def handle(
        self,
        poll_ids: t.List[int],
        delete: bool = False,
    ):
        for poll_id in poll_ids:
            try:
                poll = Poll.objects.get(pk=poll_id)
            except Poll.DoesNotExist:
                raise CommandError('Poll "%s" does not exist' % poll_id)

            poll.opened = False
            poll.save()

            self.console.print(
                f"Successfully closed poll {poll_id}",
                style="bold green",
            )

            if delete:
                poll.delete()
