from django_typer.management import TyperCommand, command, group, initialize


class Command(TyperCommand):
    @initialize()
    def init(self):
        return "upstream:init"

    @command()
    def sub1(self):
        return "upstream:sub1"

    @command()
    def sub2(self):
        return "upstream:sub2"

    @group()
    def grp1(self):
        return "upstream:grp1"

    @grp1.command()
    def grp1_cmd1(self):
        return "upstream:grp1_cmd1"
