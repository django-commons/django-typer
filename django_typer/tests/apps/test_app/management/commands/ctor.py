from django_typer import TyperCommand


class Command(TyperCommand):
    help = "Constructor tests"

    def handle(self):
        self.stderr.write(
            f"err\nno_color={self.no_color}\nforce_color={self.force_color}\n"
        )
        self.stdout.write(
            f"out\nno_color={self.no_color}\nforce_color={self.force_color}\n"
        )
