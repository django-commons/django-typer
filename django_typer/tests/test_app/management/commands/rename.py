from django_typer import TyperCommand, command


class Command(TyperCommand):
    @command(name="default")
    def handle(self):
        return "handle"

    @command(name="renamed")
    def subcommand1(self):
        return "subcommand1"

    @command("renamed2")
    def subcommand2(self):
        return "subcommand2"
