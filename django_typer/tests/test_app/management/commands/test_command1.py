import json

from django_typer import TyperCommand, callback, command


class Command(TyperCommand, add_completion=False):
    help = "This is a test help message"

    @callback(epilog="This is a test callback epilog")
    def preamble(self, pre_arg: str = "pre_arg"):
        print(f"This is a test preamble, {pre_arg}")

    @command(epilog="This is a test epilog")
    def delete(self, name: str, formal: bool = False, throw: bool = False):
        """Delete something"""
        if throw:
            raise Exception("This is a test exception")
        print(json.dumps({"name": name, "formal": formal}))

    @command(epilog="This is a test epilog")
    def create(self, name: str, number: int, switch: bool = False):
        """This is a test create command"""
        print(json.dumps({"name": name, "number": number, "switch": switch}))
