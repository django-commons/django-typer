from django.core.management import call_command
from django.test import TestCase
import pytest

from tests.utils import interact


class TestPromptOptions(TestCase):
    @pytest.mark.timeout(30)
    def test_run_with_option_prompt(self):
        cmd = interact("prompt", "--no-color", "cmd1", "bckohan")
        cmd.expect("Password:")
        cmd.sendline("test_password")
        cmd.expect("bckohan test_password")

        cmd = interact("prompt", "--no-color", "cmd2", "bckohan")
        cmd.expect("bckohan None")

        cmd = interact("prompt", "--no-color", "cmd2", "bckohan", "-p")
        cmd.expect("Password:")
        cmd.sendline("test_password2")
        cmd.expect("bckohan test_password2")

        cmd = interact("prompt", "--no-color", "cmd3", "bckohan")
        cmd.expect("bckohan default")

        cmd = interact("prompt", "--no-color", "cmd3", "bckohan", "-p")
        cmd.expect(r"Password \[default\]:")
        cmd.sendline("test_password3")
        cmd.expect("bckohan test_password3")

        cmd = interact("prompt", "--no-color", "group1", "cmd4", "bckohan")
        cmd.expect(r"Flag:")
        cmd.sendline("test_flag")
        cmd.expect(r"Password:")
        cmd.sendline("test_password4")
        cmd.expect("test_flag bckohan test_password4")

    def test_call_with_option_prompt(self):
        self.assertEqual(
            call_command(
                "prompt", "--no-color", "cmd1", "bckohan", password="test_password"
            ),
            "bckohan test_password",
        )

        self.assertEqual(
            call_command("prompt", "--no-color", "cmd2", "bckohan"), "bckohan None"
        )

        self.assertEqual(
            call_command(
                "prompt", "--no-color", "cmd2", "bckohan", "-p", "test_password2"
            ),
            "bckohan test_password2",
        )

        self.assertEqual(
            call_command("prompt", "--no-color", "cmd3", "bckohan"), "bckohan default"
        )

        self.assertEqual(
            call_command(
                "prompt", "--no-color", "cmd3", "bckohan", password="test_password3"
            ),
            "bckohan test_password3",
        )

        self.assertEqual(
            call_command(
                "prompt",
                "--no-color",
                "group1",
                "-f",
                "test_flag",
                "cmd4",
                "bckohan",
                password="test_password4",
            ),
            "test_flag bckohan test_password4",
        )

    def test_call_group_with_prompt_value(self):
        """
        This is a bug!
        """
        self.assertEqual(
            call_command(
                "prompt",
                "--no-color",
                "group1",
                "cmd4",
                "bckohan",
                flag="test_flag",
                password="test_password4",
            ),
            "test_flag bckohan test_password4",
        )
