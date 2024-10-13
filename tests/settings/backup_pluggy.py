from .backup_inherit import *

INSTALLED_APPS = [
    "tests.apps.examples.plugins.files2",
    "tests.apps.examples.plugins.files1",
    "tests.apps.examples.plugins.backup_files",
    *INSTALLED_APPS,
]
