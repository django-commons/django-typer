from django_typer.management import TyperCommand, command, group, initialize


class Command(TyperCommand):
    help = "Test staticmethods."

    @initialize(invoke_without_command=True)
    @staticmethod
    def init():
        return "init"

    @command()
    @staticmethod
    def cmd1():
        return "cmd1"

    @command()
    @staticmethod
    def cmd2():
        return "cmd2"

    @group(invoke_without_command=True)
    @staticmethod
    def grp1():
        return "grp1"

    @group(invoke_without_command=True)
    @staticmethod
    def grp2():
        return "grp2"

    @grp1.command()
    @staticmethod
    def grp1_cmd():
        return "grp1_cmd"

    @grp2.command()
    @staticmethod
    def grp2_cmd():
        return "grp2_cmd"

    @grp2.group(invoke_without_command=True)
    @staticmethod
    def grp2_subgrp():
        return "grp2_subgrp"

    @grp2_subgrp.command()
    @staticmethod
    def grp2_subgrp_cmd():
        return "grp2_subgrp_cmd"
