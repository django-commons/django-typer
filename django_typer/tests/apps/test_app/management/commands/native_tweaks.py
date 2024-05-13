from django_typer import TyperCommand
from django_typer.tests.apps.test_app.management.commands import native_self
from copy import deepcopy

Command: TyperCommand = deepcopy(getattr(native_self, "Command"))

Command.suppressed_base_arguments = {"--skip-checks", "traceback"}
