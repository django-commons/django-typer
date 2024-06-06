from .base import *

INSTALLED_APPS = [
    "tests.apps.adapter1",
    "tests.apps.adapter2",
    "tests.apps.adapter0",
    "tests.apps.test_app2",
    *INSTALLED_APPS,
]
