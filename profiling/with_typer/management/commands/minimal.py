from django_typer.management import TyperCommand


class Command(TyperCommand):
    requires_system_checks = []
    requires_migrations_checks = False

    def handle(self, test_arg: int, print: bool = False):
        if print:
            import json

            return json.dumps({"app": "with_typer", "test_arg": test_arg})
