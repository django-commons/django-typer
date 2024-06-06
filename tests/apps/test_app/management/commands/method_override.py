from django_typer.management import TyperCommand, command, initialize


class Command(TyperCommand):
    @initialize(invoke_without_command=True)
    def init(self):
        assert self.__class__ is Command
        return "test_app::init()"

    @command()
    def cmd1(self):
        """
        Command1
        """
        assert self.__class__ is Command
        return "test_app::cmd1()"

    @TyperCommand.command()  # overly verbose but tolerated
    def cmd2(self):
        """
        Command2
        """
        assert self.__class__ is Command
        return "test_app::cmd2()"
