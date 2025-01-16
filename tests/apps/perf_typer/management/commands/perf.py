from django_typer.management import TyperCommand
import sys


class Command(TyperCommand):
    requires_system_checks = []
    requires_migrations_checks = False

    def handle(self, test_arg: int, test_option: bool = False):
        return f"typer: {test_arg}, test_option={test_option}, {len(sys.modules)}"
