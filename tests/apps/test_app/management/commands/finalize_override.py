from .finalize_simple import Command as FinalizeSimple


class Command(FinalizeSimple):
    @FinalizeSimple.finalize()
    def collect(self, result, **_):
        assert isinstance(self, Command)
        assert result == "handle"
        return "collect: {}".format(result)
