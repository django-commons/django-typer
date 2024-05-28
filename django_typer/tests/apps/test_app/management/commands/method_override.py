from django_typer import TyperCommand, initialize, command


class Command(TyperCommand):
    @initialize(invoke_without_command=True)
    def init(self):
        assert self.__class__ is Command
        return f"test_app::init()"

    @command()
    def cmd1(self):
        """
        Command1
        """
        assert self.__class__ is Command
        return f"test_app::cmd1()"

    @TyperCommand.command()  # overly verbose but tolerated
    def cmd2(self):
        """
        Command2
        """
        assert self.__class__ is Command
        return f"test_app::cmd2()"
