import json

from django_typer.management import TyperCommand, command, initialize


class Command(TyperCommand):
    help = "This is a test help message"

    @initialize(epilog="This is a test callback epilog")
    def preamble(self, pre_arg: str = "pre_arg"):
        assert self.__class__ is Command
        print(f"This is a test preamble, {pre_arg}")

    @command(epilog="This is a test epilog")
    def delete(self, name: str, formal: bool = False, throw: bool = False):
        """Delete something"""
        assert self.__class__ is Command
        if throw:
            raise Exception("This is a test exception")
        print(json.dumps({"name": name, "formal": formal}))

    @command(epilog="This is a test epilog")
    def create(self, name: str, number: int, switch: bool = False):
        """This is a test create command"""
        assert self.__class__ is Command
        print(json.dumps({"name": name, "number": number, "switch": switch}))
