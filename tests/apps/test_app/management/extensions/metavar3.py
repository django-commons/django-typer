from tests.apps.test_app.management.commands.metavar3 import (
    Command as Metavar3Command,
)


@Metavar3Command.initialize(options_metavar="{INIT OVERRIDE}")
def init():
    print("init_override()")


@Metavar3Command.command(options_metavar="(CMD OVERRIDE)")
def cmd():
    return "cmd_override()"


@Metavar3Command.group(options_metavar="[GRP OVERRIDE]")
def grp():
    return "grp_override()"
