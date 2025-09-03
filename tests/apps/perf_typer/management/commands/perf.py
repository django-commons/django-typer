from django_typer.management import TyperCommand
import json
import sys


class Command(TyperCommand):
    requires_system_checks = []
    requires_migrations_checks = False

    def handle(self, test_arg: int, print: bool = False):
        if print:
            return json.dumps(
                {
                    "typer": test_arg,
                    "print": print,
                    "modules": list(sys.modules.keys()),
                }
            )
