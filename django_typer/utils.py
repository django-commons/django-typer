"""
A context manager that can be used to determine if we're executing inside of
a Typer command. This is analogous to click's get_current_context but for
command execution.
"""

# DO NOT IMPORT ANYTHING FROM TYPER HERE - SEE patch.py
from threading import local
from contextlib import contextmanager
import typing as t

_local = local()

@contextmanager
def push_command(command: "TyperCommand"):
    """
    Pushes a new command to the current stack.
    """
    _local.__dict__.setdefault("stack", []).append(command)
    try:
        yield
    finally:
        _local.stack.pop()


def get_current_command() -> t.Optional["TyperCommand"]:
    """
    Returns the current typer command. This can be used as a way to
    access the current command object from anywhere if we are executing
    inside of one from higher on the stack. We primarily need this because certain
    monkey patches are required in typer code - namely for enabling/disabling
    color based on configured parameters.

    :return: The current typer command or None if there is no active command.
    """
    try:
        return t.cast("TyperCommand", _local.stack[-1])
    except (AttributeError, IndexError) as e:
        pass
    return None
