from django_typer.management import TyperCommand, command, initialize


class Command(TyperCommand):
    @initialize()
    def init(self, common_option: bool = False):
        # you can define common options that will be available to all
        # subcommands of the command, and implement common initialization
        # logic here. This will be invoked before the chosen command
        self.common_option = common_option

    @command()
    def subcommand1(self):
        return self.common_option

    @command()
    def subcommand2(self):
        return self.common_option
