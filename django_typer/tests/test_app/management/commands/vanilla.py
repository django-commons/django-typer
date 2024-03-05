import sys

from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--exit-code", dest="exit_code", type=int, default=0)

    def handle(self, **options):
        raise sys.exit(options.get("exit_code", 0))
