from django_typer.management import TyperCommand, command


class Command(TyperCommand):
    @command(name="subcommand1")
    def handle(self):
        return "handle"

    @command()
    def subcommand2(self):
        return "subcommand2"

    @command()
    def subcommand3(self):
        return "subcommand3"
