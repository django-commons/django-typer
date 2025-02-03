from functools import partial

from django.core.management import get_commands

from . import these_strings

commands = partial(these_strings, lambda: get_commands().keys())
"""
A completer that completes management command names.

:param allow_duplicates: Whether or not to allow duplicate values. Defaults to False.
:return: A completer function.
"""
