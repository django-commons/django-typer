from django_typer.management import TyperCommand, initialize, group, finalize
from click import get_current_context


class Command(TyperCommand):
    init_opt: bool
    direct_call: bool = False

    g1_opt: bool
    g2_opt: bool

    common_kwargs = {
        "force_color",
        "no_color",
        "skip_checks",
        "version",
        "settings",
        "pythonpath",
        "traceback",
    }

    @initialize()
    def init(
        self,
        init_opt: bool = False,
        direct_call: bool = direct_call,
        call_command: bool = False,
    ):
        self.init_opt = init_opt
        self.direct_call = direct_call
        return f"root_init | init_opt={init_opt}"

    @finalize()
    def root_final(self, result, init_opt: bool, call_command: bool = False, **kwargs):
        assert isinstance(self, Command)
        if not self.direct_call:
            click_params = getattr(get_current_context(silent=True), "params", {})
            assert len(kwargs) == len(click_params) - 2
            for key, value in kwargs.items():
                assert key in click_params
                assert click_params[key] == value

        if not call_command and not self.direct_call:
            assert "g1_opt" not in kwargs
            assert "g2_opt" not in kwargs
        return f"root_final: {result} | init_opt={init_opt}"

    @group(chain=True)
    def grp1(self, g1_opt: bool = False):
        self.g1_opt = g1_opt
        return "grp1"

    @group(chain=True)
    def grp2(self, g2_opt: bool = True):
        self.g2_opt = g2_opt
        return "grp2"

    @grp1.command()
    def cmd1(self):
        return "cmd1"

    @grp1.command()
    def cmd2(self):
        return "cmd2"

    @grp2.command()
    def cmd3(self):
        return "cmd3"

    @grp2.command()
    @staticmethod
    def cmd4():
        return "cmd4"

    @grp1.finalize()
    def grp1_final(self, result, **kwargs):
        assert isinstance(self, Command)
        assert "cmd1" in result or "cmd2" in result
        assert "cmd3" not in result
        assert "cmd4" not in result
        if not self.direct_call:
            assert "g1_opt" in kwargs
            assert kwargs["g1_opt"] == self.g1_opt
            if not self.direct_call:
                for key in Command.common_kwargs:
                    assert key in kwargs
            assert "g2_opt" not in kwargs
            assert "init_opt" in kwargs
        return f"grp1_final: {result} | g1_opt={kwargs.get('g1_opt', None)}"

    @grp2.finalize()
    @staticmethod
    def grp2_final(result, **kwargs):
        assert "cmd3" in result or "cmd4" in result
        assert "cmd1" not in result
        assert "cmd2" not in result

        try:
            assert kwargs["gp2_opt"] == get_current_context().django_command.g1_opt
            for key in Command.common_kwargs:
                assert key in kwargs

            assert "g1_opt" not in kwargs
            assert "init_opt" in kwargs
        except Exception:
            pass

        return f"grp2_final: {result} | g2_opt={kwargs.get('g2_opt', None)}"
