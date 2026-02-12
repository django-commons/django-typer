"""
Test options metavar propagation and overrides
"""

from django_typer.management import TyperCommand, command, group


class Command(
    TyperCommand, options_metavar="[CLASS OPTS]", rich_markup_mode=None
):  # <-- default
    # @initialize(options_metavar="{INIT OPTS}")  # <-- override
    # def init(self):
    #     print("init")

    @command(options_metavar="<CMD OPTS>")  # <-- override
    def cmd(self):
        print("cmd")

    @group(options_metavar="(GRP OPTS)")  # <-- override
    def grp(self):
        print("grp")

    @grp.command(options_metavar="<<GRP CMD OPTS>>")  # <-- override
    def grp_cmd(self):
        print("grp cmd")

    @grp.group()  # <-- inherit from grp
    def subgrp(self):
        print("subgrp")

    @subgrp.command()  # <-- inherit from grp
    def subgrp_cmd(self):
        print("subgrp cmd")

    @subgrp.command(options_metavar="(SUBGRP CMD2 OPTS)")  # <-- override
    def subgrp_cmd2(self):
        print("subgrp cmd2")
