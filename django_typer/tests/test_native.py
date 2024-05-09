"""
Tests for the typer-native style interface.
"""

from io import StringIO

import pytest
from django import __version__ as DJANGO_VERSION
from django.core.management import call_command
from django.test import TestCase

from django_typer import get_command
from django_typer.tests.utils import run_command, similarity, rich_installed

native_help_rich = """                                              
 Usage: ./manage.py native [OPTIONS] NAME                                       
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    name      TEXT  [default: None] [required]                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Django ─────────────────────────────────────────────────────────────────────╮
│ --version                  Show program's version number and exit.           │
│ --settings           TEXT  The Python path to a settings module, e.g.        │
│                            "myproject.settings.main". If this isn't          │
│                            provided, the DJANGO_SETTINGS_MODULE environment  │
│                            variable will be used.                            │
│ --pythonpath         PATH  A directory to add to the Python path, e.g.       │
│                            "/home/djangoprojects/myproject".                 │
│                            [default: None]                                   │
│ --traceback                Raise on CommandError exceptions                  │
│ --no-color                 Don't colorize the command output.                │
│ --force-color              Force colorization of the command output.         │
│ --skip-checks              Skip system checks.                               │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

native_help_no_rich = """
Usage: ./manage.py native [OPTIONS] NAME

Arguments:
  NAME  [required]

Options:
  --version          Show program's version number and exit.
  --settings TEXT    The Python path to a settings module, e.g.
                     "myproject.settings.main". If this isn't provided, the
                     DJANGO_SETTINGS_MODULE environment variable will be used.
  --pythonpath PATH  A directory to add to the Python path, e.g.
                     "/home/djangoprojects/myproject".
  --traceback        Raise on CommandError exceptions
  --no-color         Don't colorize the command output.
  --force-color      Force colorization of the command output.
  --skip-checks      Skip system checks.
  --help             Show this message and exit.
"""

native_groups_help_rich = """                                                   
 Usage: ./manage.py native_groups [OPTIONS] COMMAND [ARGS]...                   
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Django ─────────────────────────────────────────────────────────────────────╮
│ --verbosity          INTEGER RANGE [0<=x<=3]  Verbosity level; 0=minimal     │
│                                               output, 1=normal output,       │
│                                               2=verbose output, 3=very       │
│                                               verbose output                 │
│                                               [default: 0]                   │
│ --version                                     Show program's version number  │
│                                               and exit.                      │
│ --settings           TEXT                     The Python path to a settings  │
│                                               module, e.g.                   │
│                                               "myproject.settings.main". If  │
│                                               this isn't provided, the       │
│                                               DJANGO_SETTINGS_MODULE         │
│                                               environment variable will be   │
│                                               used.                          │
│ --pythonpath         PATH                     A directory to add to the      │
│                                               Python path, e.g.              │
│                                               "/home/djangoprojects/myproje… │
│                                               [default: None]                │
│ --traceback                                   Raise on CommandError          │
│                                               exceptions                     │
│ --no-color                                    Don't colorize the command     │
│                                               output.                        │
│ --force-color                                 Force colorization of the      │
│                                               command output.                │
│ --skip-checks                                 Skip system checks.            │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ grp1                                                                         │
│ main                                                                         │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

native_groups_main_help_rich = """
 Usage: ./manage.py native_groups main [OPTIONS] NAME                            
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    name      TEXT  [default: None] [required]                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

native_groups_grp1_help_rich = """
 Usage: ./manage.py native_groups grp1 [OPTIONS] COMMAND [ARGS]...               
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --flag    --no-flag      [default: no-flag]                                  │
│ --help                   Show this message and exit.                         │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ cmd1                                                                         │
│ cmd2                                                                         │
│ subgrp                                                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

native_groups_grp1_subgrp_help_rich = """
 Usage: ./manage.py native_groups grp1 subgrp [OPTIONS] MSG COMMAND [ARGS]...    
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    msg      TEXT  [default: None] [required]                               │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

native_groups_grp1_cmd1_help_rich = """
 Usage: ./manage.py native_groups grp1 cmd1 [OPTIONS] COUNT                      
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    count      INTEGER  [default: None] [required]                          │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────
"""

native_groups_grp1_cmd2_help_rich = """
 Usage: ./manage.py native_groups grp1 cmd2 [OPTIONS] FRACTION                   
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    fraction      FLOAT  [default: None] [required]                         │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
"""


class TestNative(TestCase):
    """
    Tests that native-typer style interface works as expected.
    """

    def test_native_direct(self):
        native = get_command("native")
        self.assertEqual(native.main("Brian"), {"name": "Brian"})

    def test_native_cli(self):
        self.assertEqual(
            run_command("native", "Brian")[0].strip(), str({"name": "Brian"})
        )
        self.assertEqual(run_command("native", "--version")[0].strip(), DJANGO_VERSION)

    @pytest.mark.skipif(not rich_installed, reason="rich is not installed")
    def test_native_help_rich(self):
        stdout = StringIO()
        native = get_command("native", no_color=True, stdout=stdout)
        native.print_help("./manage.py", "native")
        sim = similarity(native_help_rich, stdout.getvalue())
        print(f"native --help similiarity: {sim}")
        self.assertGreater(sim, 0.99)

    @pytest.mark.skipif(rich_installed, reason="rich is installed")
    def test_native_help_no_rich(self):
        stdout = StringIO()
        native = get_command("native", no_color=True, stdout=stdout)
        native.print_help("./manage.py", "native")
        sim = similarity(native_help_no_rich, stdout.getvalue())
        print(f"native --help similiarity: {sim}")
        self.assertGreater(sim, 0.99)

    def test_native_call_command(self):
        self.assertEqual(call_command("native", "Brian"), {"name": "Brian"})


class TestNativeGroups(TestCase):
    @pytest.mark.skipif(not rich_installed, reason="rich is not installed")
    def test_native_groups_helps(self):
        for cmd_pth, expected_help in [
            ("native_groups", native_groups_help_rich),
            ("native_groups main", native_groups_main_help_rich),
            ("native_groups grp1", native_groups_grp1_help_rich),
            ("native_groups grp1 subgrp", native_groups_grp1_subgrp_help_rich),
            ("native_groups grp1 cmd1", native_groups_grp1_cmd1_help_rich),
            ("native_groups grp1 cmd2", native_groups_grp1_cmd2_help_rich),
        ]:
            stdout = StringIO()
            native_groups = get_command("native_groups", no_color=True, stdout=stdout)
            native_groups.print_help("./manage.py", *(cmd_pth.split()))
            sim = similarity(expected_help, stdout.getvalue())
            print(f"print_help({cmd_pth}) --help similiarity: {sim}")
            self.assertGreater(sim, 0.99)

            parts = cmd_pth.split()
            sim = similarity(
                expected_help,
                run_command(*[parts[0], "--no-color", *parts[1:]], "--help")[0].strip(),
            )
            print(f"run_command({cmd_pth}) --help similiarity: {sim}")
            self.assertGreater(sim, 0.99)

    def test_native_groups_direct(self):
        native_groups = get_command("native_groups")
        native_groups.initialize(verbosity=3)
        self.assertEqual(native_groups.main("Brian"), {"verbosity": 3, "name": "Brian"})

        native_groups.init_grp1(flag=True)

        self.assertEqual(
            native_groups.cmd1(5), {"verbosity": 3, "flag": True, "count": 5}
        )
        native_groups.cmd1(5)

        native_groups.init_grp1()
        self.assertEqual(
            native_groups.cmd2(3.5), {"verbosity": 3, "flag": False, "fraction": 3.5}
        )
        self.assertEqual(
            native_groups.run_subgrp("hello!"),
            {"verbosity": 3, "flag": False, "msg": "hello!"},
        )

    def test_native_groups_run(self):
        self.assertEqual(
            run_command("native_groups", "--verbosity", "3", "main", "Brian")[
                0
            ].strip(),
            str({"verbosity": 3, "name": "Brian"}),
        )

        self.assertEqual(
            run_command(
                "native_groups", "--verbosity", "2", "grp1", "--flag", "cmd1", "5"
            )[0].strip(),
            str({"verbosity": 2, "flag": True, "count": 5}),
        )

        self.assertEqual(
            run_command("native_groups", "--verbosity", "1", "grp1", "cmd2", "2.5")[
                0
            ].strip(),
            str({"verbosity": 1, "flag": False, "fraction": 2.5}),
        )

        self.assertEqual(
            run_command("native_groups", "grp1", "subgrp", "42!")[0].strip(),
            str({"verbosity": 0, "flag": False, "msg": "42!"}),
        )

    def test_native_groups_call(self):
        self.assertEqual(
            call_command("native_groups", "main", "Brian", verbosity=3),
            {"verbosity": 3, "name": "Brian"},
        )

        self.assertEqual(
            call_command("native_groups", "grp1", "cmd1", "5", verbosity=2, flag=True),
            {"verbosity": 2, "flag": True, "count": 5},
        )

        self.assertEqual(
            call_command("native_groups", "--verbosity", "1", "grp1", "cmd2", "2.5"),
            {"verbosity": 1, "flag": False, "fraction": 2.5},
        )

        self.assertEqual(
            call_command("native_groups", "grp1", "subgrp", "42!", flag=False),
            {"verbosity": 0, "flag": False, "msg": "42!"},
        )