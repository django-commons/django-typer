import json

from django_typer import TyperCommand, command, initialize


class Command(
    TyperCommand,
    add_completion=False,
    pretty_exceptions_enable=True,
    pretty_exceptions_show_locals=False,
    pretty_exceptions_short=False,
):
    help = "This is a test help message"

    @initialize(epilog="This is a test callback epilog")
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
