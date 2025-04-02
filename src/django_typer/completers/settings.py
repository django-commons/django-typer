"""
Completers that complete items involving Django's settings.
"""

from django.conf import settings

from . import these_strings

setting = these_strings(
    lambda: (setting for setting in dir(settings) if setting.isupper()),
    allow_duplicates=False,
)
"""
Completes Django :ref:`ref/settings:settings` names. Duplicates are not allowed.
"""

languages = these_strings(
    lambda: getattr(settings, "LANGUAGES", []) or [],
    allow_duplicates=False,
)
"""
Completes Django language codes using :setting:`LANGUAGES`. Duplicates are not allowed.
"""
