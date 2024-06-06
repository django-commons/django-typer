import typing as t

from django.core.management.base import CommandError

from django_typer.management import TyperCommand
from tests.apps.examples.polls.models import Question as Poll


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
                raise CommandError(f'Poll "{poll_id}" does not exist')

            poll.opened = False
            poll.save()

            self.stdout.write(
                self.style.SUCCESS(f'Successfully closed poll "{poll.id}"')
            )

            if delete:
                poll.delete()
