from .backup import *

INSTALLED_APPS = [
    "tests.apps.examples.plugins.my_app",
    "tests.apps.examples.plugins.media2",
    *INSTALLED_APPS,
]
