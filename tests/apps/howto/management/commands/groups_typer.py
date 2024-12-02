from django_typer.management import Typer

app = Typer()

# the normal way to add a subgroup in typer is to create a new Typer instance
# and add it to the parent group using add_typer()
grp1 = Typer()
app.add_typer(grp1, name="group1")

grp2 = Typer()
app.add_typer(grp2, name="group2")


@grp1.callback()
def group1(common_option: bool = False):
    # you can define common options that will be available to all subcommands
    # of the group, and implement common initialization logic here.
    ...


@grp2.callback()
def group2(self): ...


# attach subcommands to groups by using the command decorator on the group
# function
@grp1.command()
def grp1_subcommand1(self): ...


@grp1.command()
def grp1_subcommand2(self): ...


# this is not standard typer, but we can use the group function
# as a shortcut instead of having to create a new Typer instance
# and add it
@grp1.group()
def subgroup1(self): ...


@subgroup1.command()
def subgrp_command(self): ...
