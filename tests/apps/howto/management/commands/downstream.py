from django_typer.management import command, initialize

from .upstream import Command as Upstream


# inherit directly from the upstream command class
class Command(Upstream):
    # override init
    @initialize()
    def init(self):
        return "downstream:init"

    # override sub1
    @command()
    def sub1(self):
        return "downstream:sub1"

    # add a 3rd top level command
    @command()
    def sub3(self):
        return "downstream:sub3"

    # add a new subcommand to grp1
    @Upstream.grp1.command()
    def grp1_cmd2(self):
        return "downstream:grp1_cmd2"
