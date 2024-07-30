from django_typer.management import TyperCommand, group


class Command(TyperCommand):
    @group()
    def group1(self, common_option: bool = False):
        # you can define common options that will be available to all
        # subcommands of the group, and implement common initialization
        # logic here.
        ...

    @group()
    def group2(self): ...

    # attach subcommands to groups by using the command decorator on the group
    # function
    @group1.command()
    def grp1_subcommand1(self): ...

    @group1.command()
    def grp1_subcommand2(self): ...

    # groups can have subgroups!
    @group1.group()
    def subgroup1(self): ...

    @subgroup1.command()
    def subgrp_command(self): ...
