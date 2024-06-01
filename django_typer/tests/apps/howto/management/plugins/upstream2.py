from ..commands.upstream2 import Command as Upstream

# When plugging into an existing command we do not create
# a new class, but instead work directly with the commands
# and groups on the upstream class


# override init
@Upstream.initialize()
def init(self):
    return "plugin:init"


# override sub1
@Upstream.command()
def sub1(self):
    return "plugin:sub1"


# add a 3rd top level command
@Upstream.command()
def sub3(self):
    return "plugin:sub3"


# add a new subcommand to grp1
@Upstream.grp1.command()
def grp1_cmd2(self):
    return "plugin:grp1_cmd2"
