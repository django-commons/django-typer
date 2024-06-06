from django_typer.management import TyperCommand, command, initialize


class Command(TyperCommand):
    help = "Takes no arguments"

    suppressed_base_arguments = [
        "verbosity",
        "no_color",
        "force_color",
        "help",
        "settings",
        "pythonpath",
        "traceback",
        "version",
        "skip_checks",
    ]

    @initialize()
    def init(self):
        assert self.__class__ is Command

    @command(add_help_option=False)
    def cmd(self):
        assert self.__class__ is Command
