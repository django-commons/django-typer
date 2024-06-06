from django_typer.management import TyperCommand


class Command(TyperCommand):
    help = "Do nothing"

    def handle(self):
        assert self.__class__ is Command
