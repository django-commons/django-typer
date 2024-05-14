from django.core.management import call_command, CommandError
from django.test import TestCase, override_settings

from django_typer import get_command
from django_typer.tests.utils import run_command, rich_installed, similarity


@override_settings(
    INSTALLED_APPS=[
        "django_typer.tests.apps.adapter0",
        "django_typer.tests.apps.test_app2",
        "django_typer.tests.apps.test_app",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
)
class InterferenceTests(TestCase):
    """
    commands can be adapted by extending or overriding them. However, when done
    this should *not* affect the root command. These tests test that the root
    command can be imported and used directly even when it is extended by apps
    further up the app stack.

    TODO - if we can fix the argument name interference problem, this would be a
    good test to also test that - just rename all the arguments in the command to arg#.
    """

    def test_inherit_command_interfence(self):
        self.assertEqual(
            call_command("interference", "cmd1", "abc"),
            "test_app::interference::cmd1(abc)",
        )
        self.assertEqual(
            call_command("interference_ext", "cmd1", "5"),
            "test_app2::interference::cmd1(5)",
        )

        self.assertEqual(
            call_command("interference", "cmd2", "10"),
            "test_app::interference::cmd2(10)",
        )
        self.assertEqual(
            call_command("interference_ext", "cmd2", "10"),
            "test_app::interference::cmd2(10)",
        )

        self.assertEqual(
            call_command("interference_ext", "cmd-ext"),
            "test_app2::interference::cmd_ext()",
        )
        with self.assertRaises(CommandError):
            call_command("interference", "cmd-ext")

        with self.assertRaises(CommandError):
            call_command("interference", "adapt-cmd")

        self.assertEqual(
            call_command("interference_ext", "adapt-cmd"),
            "test_app2::interference::adapt_cmd()",
        )

    def test_inherit_group_interfence(self):
        self.assertEqual(
            call_command("interference", "grp1", "1.2"),
            "test_app::interference::grp1(1.2)",
        )
        self.assertEqual(
            call_command("interference", "grp1", "1.3", "cmd3", "abc", "def"),
            "test_app::interference::grp1(1.3)::cmd3(abc, def)",
        )
        self.assertEqual(
            call_command("interference", "grp1", "1.4", "cmd4", "3", "7"),
            "test_app::interference::grp1(1.4)::cmd4(3, 7)",
        )
        self.assertEqual(
            call_command("interference", "grp1", "1.4", "subgroup", "--arg5-0"),
            "test_app::interference::grp1(1.4)::subgroup(True)",
        )
        self.assertEqual(
            call_command("interference", "grp1", "1.4", "subgroup", "--arg5-0"),
            "test_app::interference::grp1(1.4)::subgroup(True)",
        )
        self.assertEqual(
            call_command(
                "interference",
                "grp1",
                "1.4",
                "subgroup",
                "subsubgroup",
                "subsubcommand",
            ),
            "test_app::interference::grp1(1.4)::subgroup(False)::subsubgroup(True)::subsubcommand()",
        )
        with self.assertRaises(CommandError):
            call_command("interference", "grp2", "xyz")

        with self.assertRaises(CommandError):
            call_command("interference", "grp1", "1.4", "subgroup", "--arg5-0", "cmd5")

        with self.assertRaises(CommandError):
            call_command(
                "interference",
                "grp1",
                "1.4",
                "subgroup",
                "subsubgroup",
                "subsubcommand2",
            )

        with self.assertRaises(CommandError):
            call_command("interference", "adapt-group")

        with self.assertRaises(CommandError):
            call_command("interference", "subgroup")

        with self.assertRaises(CommandError):
            call_command("interference", "subsubgroup")

        self.assertEqual(
            call_command("interference_ext", "grp1", "1.2"),
            "test_app::interference::grp1(1.2)",
        )
        self.assertEqual(
            call_command("interference_ext", "grp1", "2.5", "cmd3", "8", "9"),
            "test_app2::interference::grp1(2.5)::cmd3(8, 9)",
        )
        self.assertEqual(
            call_command("interference_ext", "grp1", "1.4", "cmd4", "3", "7"),
            "test_app::interference::grp1(1.4)::cmd4(3, 7)",
        )
        self.assertEqual(
            call_command("interference_ext", "grp2", "xyz"),
            "test_app2::interference::grp2(xyz)",
        )
        self.assertEqual(
            call_command(
                "interference_ext", "grp1", "1.4", "subgroup", "--arg5-0", "cmd5"
            ),
            "test_app2::interference::grp1(1.4)::subgroup(True)::cmd5()",
        )
        self.assertEqual(
            call_command(
                "interference_ext",
                "grp1",
                "1.4",
                "subgroup",
                "subsubgroup",
                "subsubcommand",
            ),
            "test_app2::interference::grp1(1.4)::subgroup(False)::subsubgroup(True)::subsubcommand()",
        )
        self.assertEqual(
            call_command(
                "interference_ext",
                "grp1",
                "1.4",
                "subgroup",
                "subsubgroup",
                "subsubcommand2",
            ),
            "test_app2::interference::grp1(1.4)::subgroup(False)::subsubgroup(True)::subsubcommand2()",
        )
        self.assertEqual(
            call_command("interference_ext", "adapt-group"),
            "test_app2::interference::adapt_group()",
        )

        with self.assertRaises(CommandError):
            call_command("interference_ext", "subgroup")

        with self.assertRaises(CommandError):
            call_command("interference_ext", "subsubgroup")

    def test_inherit_initialize_interference(self):
        self.assertEqual(
            call_command("interference"), "test_app::interference::init(True)"
        )
        self.assertEqual(
            call_command("interference_ext"), "test_app2::interference::init(True)"
        )
