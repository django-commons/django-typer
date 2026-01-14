"""
Test options metavar propagation and overrides
"""

from .metavar import Command as MetavarCommand


class Command(MetavarCommand, options_metavar="{SUBCLASS OPTS}"):
    pass
