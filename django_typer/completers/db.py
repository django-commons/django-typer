from functools import partial

from django.conf import settings

from . import these_strings

# use a function that returns a generator because we should not access settings on
# import
databases = partial(these_strings, lambda: settings.DATABASES.keys())
"""
A completer that completes Django database aliases configured in settings.DATABASES.

:param allow_duplicates: Whether or not to allow duplicate values. Defaults to False.
:return: A completer function.
"""
