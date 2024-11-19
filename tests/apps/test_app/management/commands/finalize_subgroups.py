from django_typer.management import TyperCommand, command, group, finalize


class Command(TyperCommand):
    @finalize()
    def root_final(self, result, **_):
        assert isinstance(self, Command)
        assert result == "handle"
        return "root_final"

    @group()
    def grp1(self):
        return "grp1"

    @group()
    def grp2(self):
        return "grp2"

    @grp1.command()
    def cmd1(self):
        return "cmd1"

    @grp1.command()
    def cmd2(self):
        return "cmd2"

    @grp2.command()
    def cmd3(self):
        return "cmd3"

    @grp2.command()
    def cmd4(self):
        return "cmd4"

    @grp1.finalize()
    def grp1_final(self, result, **_):
        assert isinstance(self, Command)
        assert result in ["cmd1", "cmd2"]
        return "grp1_final"

    @grp2.finalize()
    def grp2_final(self, result, **_):
        assert isinstance(self, Command)
        assert result in ["cmd3", "cmd4"]
        return "grp2_final"
