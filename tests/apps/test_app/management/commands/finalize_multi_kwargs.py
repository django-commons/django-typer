from django_typer.management import TyperCommand, command, finalize
from click import get_current_context


class Command(TyperCommand, chain=True):
    suppressed_base_arguments = {
        "verbosity",
        "skip_checks",
        "version",
        "settings",
        "pythonpath",
    }

    @finalize()
    def final(self, result, **kwargs):
        assert isinstance(self, Command)
        click_params = getattr(get_current_context(silent=True), "params", {})
        assert len(kwargs) == len(click_params)
        for key, value in kwargs.items():
            assert key in click_params
            assert click_params[key] == value
        return "finalized: {} | {}".format(result, kwargs)

    @command()
    def cmd1(self, arg1: int = 1):
        return "cmd1 {}".format(arg1)

    @command()
    def cmd2(self, arg2: int):
        return "cmd2 {}".format(arg2)
