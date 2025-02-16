import pytest
from django.test import TestCase, override_settings

from django_typer.management import get_command
from tests.utils import rich_installed, run_command, similarity

basic_help = """
 Usage: ./manage.py basic [OPTIONS] ARG1 ARG2                                   
                                                                                
 A basic command that uses Typer                                                
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    arg1      TEXT  [default: None] [required]                              │
│ *    arg2      TEXT  [default: None] [required]                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --arg3        FLOAT    [default: 0.5]                                        │
│ --arg4        INTEGER  [default: 1]                                          │
│ --help                 Show this message and exit.                           │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Django ─────────────────────────────────────────────────────────────────────╮
│ --version                  Show program's version number and exit.           │
│ --settings           TEXT  The Python path to a settings module, e.g.        │
│                            "myproject.settings.main". If this isn't          │
│                            provided, the DJANGO_SETTINGS_MODULE environment  │
│                            variable will be used.                            │
│ --pythonpath         PATH  A directory to add to the Python path, e.g.       │
│                            "/home/djangoprojects/myproject".                 │
│ --traceback                Raise on CommandError exceptions                  │
│ --show-locals              Print local variables in tracebacks.              │
│ --no-color                 Don't colorize the command output.                │
│ --force-color              Force colorization of the command output.         │
│ --skip-checks              Skip system checks.                               │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

basic_help_no_rich = """
Usage: ./manage.py basic [OPTIONS] ARG1 ARG2

  A basic command that uses Typer

Arguments:
  ARG1  [required]
  ARG2  [required]

Options:
  --arg3 FLOAT       [default: 0.5]
  --arg4 INTEGER     [default: 1]
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

multi_help_no_rich = """
Usage: ./manage.py multi [OPTIONS] COMMAND [ARGS]...
  
  A command that defines subcommands.

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

Commands:
  create  Create an object.
  delete  Delete an object.
"""

multi_create_help_no_rich = """
Usage: ./manage.py multi create [OPTIONS] NAME

  Create an object.

Arguments:
  NAME  The name of the object to create.  [required]

Options:
  --help  Show this message and exit.
"""

multi_delete_help_no_rich = """
Usage: ./manage.py multi delete [OPTIONS] ID

  Delete an object.

Arguments:
  ID  The id of the object to delete.  [required]

Options:
  --help  Show this message and exit.
"""

multi_help = """
 Usage: ./manage.py multi [OPTIONS] COMMAND [ARGS]...                           
 
  A command that defines subcommands.

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
│ --traceback                Raise on CommandError exceptions                  │
│ --show-locals              Print local variables in tracebacks.              │
│ --no-color                 Don't colorize the command output.                │
│ --force-color              Force colorization of the command output.         │
│ --skip-checks              Skip system checks.                               │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ create   Create an object.                                                   │
│ delete   Delete an object.                                                   │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

multi_create_help = """
 Usage: ./manage.py multi create [OPTIONS] NAME                                 
                                                                                
 Create an object.                                                              
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    name      TEXT  The name of the object to create. [default: None]       │
│                      [required]                                              │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

multi_delete_help = """
 Usage: ./manage.py multi delete [OPTIONS] ID                                   
                                                                                
 Delete an object.                                                              
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    id      INTEGER  The id of the object to delete. [default: None]        │
│                       [required]                                             │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

hierarchy_help = """
 Usage: ./manage.py hierarchy [OPTIONS] COMMAND [ARGS]...                       
                                                                                
 A more complex command that defines a hierarchy of subcommands.                
                                                                                
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
│ --traceback                Raise on CommandError exceptions                  │
│ --show-locals              Print local variables in tracebacks.              │
│ --no-color                 Don't colorize the command output.                │
│ --force-color              Force colorization of the command output.         │
│ --skip-checks              Skip system checks.                               │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ math   Do some math at the given precision.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

hierarchy_help_no_rich = """
Usage: ./manage.py hierarchy [OPTIONS] COMMAND [ARGS]...

  A more complex command that defines a hierarchy of subcommands.

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

Commands:
  math  Do some math at the given precision.
"""

hierarchy_math_help = """
 Usage: ./manage.py hierarchy math [OPTIONS] COMMAND [ARGS]...                  
                                                                                
 Do some math at the given precision.                                           
                                                                                
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --precision        INTEGER  The number of decimal places to output.          │
│                             [default: 2]                                     │
│ --help                      Show this message and exit.                      │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Commands ───────────────────────────────────────────────────────────────────╮
│ divide     Divide the given numbers.                                         │
│ multiply   Multiply the given numbers.                                       │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

hierarchy_math_divide_help = """
 Usage: ./manage.py hierarchy math divide [OPTIONS] NUMERATOR DENOMINATOR       
                                                                                
 Divide the given numbers.                                                      
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    numerator        FLOAT  The numerator [default: None] [required]        │
│ *    denominator      FLOAT  The denominator [default: None] [required]      │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --floor    --no-floor      Use floor division [default: no-floor]            │
│ --help                     Show this message and exit.                       │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

hierarchy_math_multiply_help = """
 Usage: ./manage.py hierarchy math multiply [OPTIONS] NUMBERS...                
                                                                                
 Multiply the given numbers.                                                    
                                                                                
╭─ Arguments ──────────────────────────────────────────────────────────────────╮
│ *    numbers      NUMBERS...  The numbers to multiply [default: None]        │
│                               [required]                                     │
╰──────────────────────────────────────────────────────────────────────────────╯
╭─ Options ────────────────────────────────────────────────────────────────────╮
│ --help          Show this message and exit.                                  │
╰──────────────────────────────────────────────────────────────────────────────╯
"""

hierarchy_math_help_no_rich = """
Usage: ./manage.py hierarchy math [OPTIONS] COMMAND [ARGS]...

  Do some math at the given precision.

Options:
  --precision INTEGER  The number of decimal places to output.  [default: 2]
  --help               Show this message and exit.

Commands:
  divide    Divide the given numbers.
  multiply  Multiply the given numbers.
"""

hierarchy_math_divide_help_no_rich = """
Usage: ./manage.py hierarchy math divide [OPTIONS] NUMERATOR DENOMINATOR

  Divide the given numbers.

Arguments:
  NUMERATOR    The numerator  [required]
  DENOMINATOR  The denominator  [required]

Options:
  --floor / --no-floor  Use floor division  [default: no-floor]
  --help                Show this message and exit.
"""

hierarchy_math_multiply_help_no_rich = """
Usage: ./manage.py hierarchy math multiply [OPTIONS] NUMBERS...

  Multiply the given numbers.

Arguments:
  NUMBERS...  The numbers to multiply  [required]

Options:
  --help  Show this message and exit.
"""


class ExampleTests(TestCase):
    settings = "tests.settings.examples"

    @pytest.mark.rich
    @pytest.mark.no_rich
    def test_basic(self):
        observed_help = run_command(
            "basic", "--settings", self.settings, "--no-color", "--help"
        )[0].strip()
        self.assertGreater(
            similarity(
                observed_help, basic_help if rich_installed else basic_help_no_rich
            ),
            0.99,
        )

    @pytest.mark.rich
    @pytest.mark.no_rich
    def test_multi(self):
        observed_help = run_command(
            "multi", "--settings", self.settings, "--no-color", "--help"
        )[0].strip()
        self.assertGreater(
            similarity(
                observed_help, multi_help if rich_installed else multi_help_no_rich
            ),
            0.99,
        )

        observed_help = run_command(
            "multi", "--settings", self.settings, "--no-color", "create", "--help"
        )[0].strip()
        self.assertGreater(
            similarity(
                observed_help,
                multi_create_help if rich_installed else multi_create_help_no_rich,
            ),
            0.99,
        )

        observed_help = run_command(
            "multi", "--settings", self.settings, "--no-color", "delete", "--help"
        )[0].strip()
        self.assertGreater(
            similarity(
                observed_help,
                multi_delete_help if rich_installed else multi_delete_help_no_rich,
            ),
            0.99,
        )

    @pytest.mark.rich
    @pytest.mark.no_rich
    def test_hierarchy(self):
        observed_help = run_command(
            "hierarchy", "--settings", self.settings, "--no-color", "--help"
        )[0].strip()
        self.assertGreater(
            similarity(
                observed_help,
                hierarchy_help if rich_installed else hierarchy_help_no_rich,
            ),
            0.99,
        )

        observed_help = run_command(
            "hierarchy", "--settings", self.settings, "--no-color", "math", "--help"
        )[0].strip()
        self.assertGreater(
            similarity(
                observed_help,
                hierarchy_math_help if rich_installed else hierarchy_math_help_no_rich,
            ),
            0.99,
        )

        observed_help = run_command(
            "hierarchy",
            "--settings",
            self.settings,
            "--no-color",
            "math",
            "divide",
            "--help",
        )[0].strip()
        self.assertGreater(
            similarity(
                observed_help,
                hierarchy_math_divide_help
                if rich_installed
                else hierarchy_math_divide_help_no_rich,
            ),
            0.99,
        )

        observed_help = run_command(
            "hierarchy",
            "--settings",
            self.settings,
            "--no-color",
            "math",
            "multiply",
            "--help",
        )[0].strip()
        try:
            self.assertGreater(
                similarity(
                    observed_help,
                    hierarchy_math_multiply_help
                    if rich_installed
                    else hierarchy_math_multiply_help_no_rich,
                ),
                0.99,
            )
        except AssertionError:
            import ipdb

            ipdb.set_trace()

        self.assertEqual(
            run_command(
                "hierarchy",
                "--settings",
                self.settings,
                "--no-color",
                "math",
                "--precision",
                "4",
                "multiply",
                "3",
                "7",
                parse_json=False,
            )[0].strip(),
            "21.0000",
        )

        self.assertEqual(
            run_command(
                "hierarchy",
                "--settings",
                self.settings,
                "--no-color",
                "math",
                "--precision",
                "4",
                "divide",
                "3",
                "7",
                parse_json=False,
            )[0].strip(),
            "0.4286",
        )


class TyperExampleTests(ExampleTests):
    settings = "tests.settings.typer_examples"


@override_settings(
    INSTALLED_APPS=[
        "tests.apps.examples.completers",
        "tests.apps.examples.basic",
        "django_typer",
        "django.contrib.admin",
        "django.contrib.auth",
        "django.contrib.contenttypes",
        "django.contrib.sessions",
        "django.contrib.messages",
        "django.contrib.staticfiles",
    ]
)
class CompleterExampleTests(TestCase):
    app_labels_cmd = "app_labels"

    def test_app_labels_completer(self):
        from django_typer.management.commands.shellcompletion import (
            Command as ShellCompletion,
        )

        shellcompletion = get_command("shellcompletion", ShellCompletion).init(
            shell="zsh"
        )
        completions = shellcompletion.complete(f"{self.app_labels_cmd} ")
        self.assertTrue("contenttypes" in completions)
        self.assertTrue("completers" in completions)
        self.assertTrue("django_typer" in completions)
        self.assertTrue("admin" in completions)
        self.assertTrue("auth" in completions)
        self.assertTrue("sessions" in completions)
        self.assertTrue("messages" in completions)

        completions = shellcompletion.complete(f"{self.app_labels_cmd} a")

        self.assertTrue("admin" in completions)
        self.assertTrue("auth" in completions)

        stdout, stderr, retcode = run_command(
            self.app_labels_cmd,
            "--settings",
            "tests.settings.examples",
            "admin",
            "auth",
        )
        self.assertEqual(retcode, 0, msg=stderr)
        self.assertEqual(stdout.strip(), str(["admin", "auth"]))


class CompleterTyperExampleTests(CompleterExampleTests):
    app_labels_cmd = "app_labels_typer"
