from django_typer import TyperCommand


class Command(TyperCommand):
    help = "Return an object"

    def handle(self):
        return {"key": "value"}
