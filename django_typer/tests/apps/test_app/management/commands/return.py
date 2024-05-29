from django_typer import TyperCommand


class Command(TyperCommand):
    help = "Return an object"

    def handle(self):
        assert self.__class__ is Command
        return {"key": "value"}
