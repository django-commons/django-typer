from django_typer.utils import register_command_plugins
from tests.apps.examples.plugins.backup.management.commands.backup import Command as Backup
from tests.apps.examples.plugins.media2.management import plugins as media2_plugins
from tests.apps.examples.plugins.my_app.management import plugins as my_app_plugins

register_command_plugins(media2_plugins)
register_command_plugins(my_app_plugins)

app = Backup().typer_app

# todo necessary?