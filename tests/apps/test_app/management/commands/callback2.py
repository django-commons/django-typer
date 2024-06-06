import json

from django_typer.management import TyperCommand, callback, command


class Command(TyperCommand, invoke_without_command=True):
    help = "Test basic callback command."

    parameters = {}

    @callback(
        context_settings={
            "allow_interspersed_args": True,
            "ignore_unknown_options": True,
        }
    )
    def init(self, p1: int, flag1: bool = False, flag2: bool = True):
        """
        The callback to initialize the command.
        """
        assert self.__class__ is Command
        self.parameters = {"p1": p1, "flag1": flag1, "flag2": flag2}
        return json.dumps(self.parameters)

    @command(
        context_settings={
            "allow_interspersed_args": True,
            "ignore_unknown_options": True,
        }
    )
    def handle(self, arg1: str, arg2: str, arg3: float = 0.5, arg4: int = 1):
        assert self.__class__ is Command
        self.parameters.update({"arg1": arg1, "arg2": arg2, "arg3": arg3, "arg4": arg4})
        return json.dumps(self.parameters)
