import os

import django

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "django_typer.tests.settings")
django.setup()


from django_typer.tests.test_app.management.commands.groups import (
    Command as GroupCommand,
)

group = GroupCommand()

group.echo("hello")

group.math(3)
