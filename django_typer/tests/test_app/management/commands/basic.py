import json
from django_typer import TyperCommand


class Command(TyperCommand):
    
    help = 'Test minimal TyperCommand subclass'

    def handle(self, arg1: str, arg2: str, arg3: float = 0.5, arg4: int = 1):
        opts = {
            'arg1': arg1,
            'arg2': arg2,
            'arg3': arg3,
            'arg4': arg4
        }
        return json.dumps(opts)
