from django_typer.management import TyperCommand, command


class Command(TyperCommand):
    help = "Test various forms of handle override."

    @command()
    def handle(self) -> str:
        assert self.__class__ is Command
        return "handle2"
