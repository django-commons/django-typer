from tests.apps.test_app.management.commands.adapted import (
    Command as Adapted,
)


@Adapted.command(name="echo")
def new_echo(self, msg1: str, msg2: str):
    """
    Echo both messages.
    """
    assert self.__class__ is Adapted
    self.echo(f"test_app2: {msg1} {msg2}")


@Adapted.command()
def no_self(int1: int, int2: int):
    assert isinstance(int1, int)
    assert isinstance(int2, int)
    print(f"test_app2: {int1, int2}")
