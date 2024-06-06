from django_typer.management import TyperCommand, command


class Command(TyperCommand):
    @command(name="default")
    def handle(self):
        assert self.__class__ is Command
        return "handle"

    @command(name="renamed")
    def subcommand1(self):
        assert self.__class__ is Command
        return "subcommand1"

    @command("renamed2")
    def subcommand2(self):
        assert self.__class__ is Command
        return "subcommand2"
