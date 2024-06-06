from django.utils import timezone

from django_typer.management import TyperCommand
from tests.apps.examples.polls.models import Question as Poll


class Command(TyperCommand):
    help = "Create some test polls"

    def handle(self):
        self.q1 = Poll.objects.create(
            question_text="What is your favorite ice cream?",
            pub_date=timezone.now(),
        )
        self.q2 = Poll.objects.create(
            question_text="Messi or Ronaldo?",
            pub_date=timezone.now(),
        )
        self.q3 = Poll.objects.create(
            question_text="What about quests?!",
            pub_date=timezone.now(),
        )
