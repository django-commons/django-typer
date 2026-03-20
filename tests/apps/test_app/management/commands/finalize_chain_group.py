from django_typer.management import TyperCommand, group, command, finalize, Context


class Command(TyperCommand, chain=True):
    @finalize()
    def root_final(self, result):
        assert isinstance(self, Command)
        return f"root_final: {result}"

    @command()
    def cmd1(self, arg1: int = 1):
        return f"cmd1 {arg1}"

    @command()
    def cmd2(self, arg2: int = 2):
        return f"cmd2 {arg2}"

    @group(chain=True, invoke_without_command=True)
    def grp(self, ctx: Context):
        if ctx.invoked_subcommand is None:
            results = []
            for name, cmd in ctx.command.commands.items():
                # Create a sub-context and invoke
                sub_ctx = Context(cmd, parent=ctx)
                if name == "cmd4":
                    sub_ctx.params = {"arg4": 5}
                results.append(cmd.invoke(sub_ctx))
            return results

    @grp.command()
    def cmd3(self, arg3: int = 3):
        return f"cmd3 {arg3}"

    @grp.command()
    def cmd4(self, ctx: Context, arg4: int = 4):
        return f"cmd4 {arg4}"

    @grp.finalize()
    def grp_final(self, result):
        assert isinstance(self, Command)
        return f"grp_final: {result}"
