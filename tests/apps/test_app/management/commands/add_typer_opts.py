"""
Sub-app settings given to the Typer constructor or its callback must survive
add_typer() when they are not repeated there - see issue #256.
"""

from django_typer.management import Typer, TyperCommand

Command: TyperCommand

app = Typer()


@app.command()
def top():
    return "top"


# settings on the sub-app instance
inst = Typer(
    name="inst",
    help="Instance help.",
    rich_help_panel="Instance Panel",
    deprecated=True,
    options_metavar="[INST OPTS]",
)


@inst.command()
def leaf1():
    return "leaf1"


# settings on the sub-app callback
cb = Typer(name="cb")


@cb.callback(
    rich_help_panel="Callback Panel", deprecated=True, options_metavar="[CB OPTS]"
)
def cb_init():
    pass


@cb.command()
def leaf2():
    return "leaf2"


# explicit add_typer() arguments still win over both
expl = Typer(
    name="expl",
    rich_help_panel="Ignored Panel",
    deprecated=True,
    options_metavar="[IGNORED OPTS]",
)


@expl.command()
def leaf3():
    return "leaf3"


app.add_typer(inst)
app.add_typer(cb)
app.add_typer(
    expl,
    rich_help_panel="Explicit Panel",
    deprecated=False,
    options_metavar="[EXPL OPTS]",
)
