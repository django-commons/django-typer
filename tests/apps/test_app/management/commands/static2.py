from django_typer.management import TyperCommand, command, group, initialize


class Command(TyperCommand):
    help = "Test staticmethods."

    @initialize(invoke_without_command=True)
    def init():
        return "init"

    @command()
    def cmd1():
        return "cmd1"

    @command()
    def cmd2():
        return "cmd2"

    @group(invoke_without_command=True)
    def grp1():
        return "grp1"

    @group(invoke_without_command=True)
    def grp2():
        return "grp2"

    @grp1.command()
    def grp1_cmd():
        return "grp1_cmd"

    @grp2.command()
    def grp2_cmd():
        return "grp2_cmd"

    @grp2.group(invoke_without_command=True)
    def grp2_subgrp():
        return "grp2_subgrp"

    @grp2_subgrp.command()
    def grp2_subgrp_cmd():
        return "grp2_subgrp_cmd"
