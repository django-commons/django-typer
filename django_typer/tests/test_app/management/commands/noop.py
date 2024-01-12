from django_typer import TyperCommand


class Command(TyperCommand):
    help = "Do nothing"

    def handle(self):
        pass
