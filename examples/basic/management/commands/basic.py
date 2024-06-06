from django_typer.management import TyperCommand


class Command(TyperCommand):
    def handle(self, arg1: str, arg2: str, arg3: float = 0.5, arg4: int = 1):
        """
        A basic command that uses Typer
        """
