from django.core.management.base import BaseCommand, CommandParser
import sys
import json


class Command(BaseCommand):
    requires_system_checks = []
    requires_migrations_checks = False

    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("test_arg", type=int)
        parser.add_argument("--test-option", action="store_true")
        return super().add_arguments(parser)

    def handle(self, test_arg, test_option, **_):
        return json.dumps(
            {
                "no_typer": test_arg,
                "test_option": test_option,
                "modules": list(sys.modules.keys()),
            }
        )
