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
    def final(
        self, result, force_color=None, no_color=None, traceback=None, show_locals=None
    ):
        assert isinstance(self, Command)
        try:
            click_params = getattr(get_current_context(silent=False), "params", {})
            assert "force_color" in click_params
            assert click_params["force_color"] == force_color
            assert "no_color" in click_params
            assert click_params["no_color"] == no_color
            assert "traceback" in click_params
            assert click_params["traceback"] == traceback
            assert "show_locals" in click_params
            assert click_params["show_locals"] == traceback
        except Exception:
            pass
        return "finalized: {} | {}".format(
            result,
            {
                "force_color": force_color,
                "no_color": no_color,
                "traceback": traceback,
                "show_locals": show_locals,
            },
        )

    @command()
    def cmd1(self, arg1: int = 1):
        return "cmd1 {}".format(arg1)

    @command()
    def cmd2(self, arg2: int):
        return "cmd2 {}".format(arg2)
