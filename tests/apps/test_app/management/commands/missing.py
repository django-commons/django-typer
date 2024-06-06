from django.utils.translation import gettext_lazy as _

from django_typer.management import TyperCommand


class Command(TyperCommand):
    help = "Test missing parameter."

    missing_args_message = _("{parameter} must be given.")

    def handle(self, arg1: int):
        pass
