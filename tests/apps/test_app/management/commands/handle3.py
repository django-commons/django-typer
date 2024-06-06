from .handle import Command as Handle


class Command(Handle):
    help = "Test various forms of handle override."

    def handle(self) -> str:
        assert self.__class__ is Command
        return "handle3"
