from django_typer.management import TyperCommand
import json
import sys


class Command(TyperCommand):
    requires_system_checks = []
    requires_migrations_checks = False

    def handle(self, test_arg: int, test_option: bool = False):
        return json.dumps(
            {
                "typer": test_arg,
                "test_option": test_option,
                "modules": list(sys.modules.keys()),
            }
        )
