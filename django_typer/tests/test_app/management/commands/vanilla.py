import json
from pprint import pprint

from django.core.management.base import BaseCommand, CommandParser


class Command(BaseCommand):
    def add_arguments(self, parser: CommandParser) -> None:
        parser.add_argument("--name", type=str)

    def handle(self, **options):
        pprint(json.dumps(options))
