from django_typer.management import TyperCommand, command


# here we pass chain=True to typer telling it to allow invocation of
# multiple subcommands
class Command(TyperCommand, chain=True):
    @command()
    def cmd1(self):
        self.stdout.write("cmd1")

    @command()
    def cmd2(self):
        self.stdout.write("cmd2")
