from django_typer.utils import register_command_plugins
from django_typer.tests.apps.examples.extensions.backup.management.commands.backup import Command as Backup
from django_typer.tests.apps.examples.extensions.media2.management import extensions as media2_plugins
from django_typer.tests.apps.examples.extensions.my_app.management import extensions as my_app_plugins

register_command_plugins(media2_plugins)
register_command_plugins(my_app_plugins)

app = Backup().typer_app

# todo necessary?