from django.test import TestCase

from django_typer.management import get_command
from django_typer.utils import get_current_command


class TestGetCommand(TestCase):
    def test_get_command(self):
        from tests.apps.test_app.management.commands.basic import (
            Command as Basic,
        )

        basic = get_command("basic")
        assert basic.__class__ == Basic

        from tests.apps.test_app.management.commands.multi import (
            Command as Multi,
        )

        multi = get_command("multi")
        assert multi.__class__ == Multi
        cmd1 = get_command("multi", "cmd1")
        assert cmd1.__func__ is multi.cmd1.__func__
        sum = get_command("multi", "sum")
        assert sum.__func__ is multi.sum.__func__
        cmd3 = get_command("multi", "cmd3")
        assert cmd3.__func__ is multi.cmd3.__func__

        from tests.apps.test_app.management.commands.callback1 import (
            Command as Callback1,
        )

        callback1 = get_command("callback1")
        assert callback1.__class__ == Callback1

        # callbacks are not commands
        with self.assertRaises(LookupError):
            get_command("callback1", "init")


def test_get_current_command_returns_none():
    assert get_current_command() is None
