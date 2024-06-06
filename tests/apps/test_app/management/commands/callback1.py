import json

from django_typer.management import TyperCommand, initialize


class Command(TyperCommand):
    help = "Test basic callback command."

    parameters = {}

    @initialize()
    def init(self, p1: int, flag1: bool = False, flag2: bool = True):
        """
        The callback to initialize the command.
        """
        assert self.__class__ is Command
        self.parameters = {"p1": p1, "flag1": flag1, "flag2": flag2}

    def handle(self, arg1: str, arg2: str, arg3: float = 0.5, arg4: int = 1):
        assert self.__class__ is Command
        self.parameters.update({"arg1": arg1, "arg2": arg2, "arg3": arg3, "arg4": arg4})
        return json.dumps(self.parameters)
