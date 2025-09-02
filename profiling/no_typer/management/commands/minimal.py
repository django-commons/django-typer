from django.core.management import BaseCommand


class Command(BaseCommand):
    requires_system_checks = []
    requires_migrations_checks = False

    def add_arguments(self, parser) -> None:
        parser.add_argument("test_arg", type=int)
        parser.add_argument("--print", action="store_true")
        return super().add_arguments(parser)

    def handle(self, test_arg, print, **_):
        if print:
            import json

            return json.dumps(
                {
                    "app": "no_typer",
                    "test_arg": test_arg,
                }
            )
