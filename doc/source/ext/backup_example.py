from django_typer.utils import register_command_extensions
from django_typer.tests.apps.examples.extensions.backup.management.commands.backup import Command as Backup
from django_typer.tests.apps.examples.extensions.media2.management import extensions as media2_extensions
from django_typer.tests.apps.examples.extensions.my_app.management import extensions as my_app_extensions

register_command_extensions(media2_extensions)
register_command_extensions(my_app_extensions)

app = Backup().typer_app
