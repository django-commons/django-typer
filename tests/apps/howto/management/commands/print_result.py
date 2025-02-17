from django_typer.management import TyperCommand


class Command(TyperCommand):
    print_result = False

    def handle(self):
        return "This will not be printed"
