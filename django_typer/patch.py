"""
Mostly because typer does not allow direct access to the rich console objects it
creates we need to do some monkey patching to get the desired behavior when
--no-color options or --force-color options are specified

apply() needs to be called before any imports from Typer

.. todo::
    
    Revisit this if Typer exposes control of the console objects.

To achieve expected --force-color and --no-color behavior there are 3 different
console objects installed when rich is used:

- The first is the global exception handler installed by rich - see apps.py
- The second is the command exception handler console installed by typer - see below
- The third is the console used by the command itself to output helps - see below

"""

import os
import sys
from django_typer.utils import get_current_command
from click import get_current_context

patch_applied = False

def apply():
    """
    Apply monkey patches to get our console objects to recognize django's --no-color
    and --force-color options. This is non critical code, so we wrap the entire thing
    in a global exception handler and punt if it fails.
    """
    global patch_applied
    if patch_applied:
        return
    patch_applied = True
    try:
        from rich.console import Console
        # this has to go here before rich Consoles are instantiated by Typer
        color_system = 'auto'
        force_terminal = None
        if "--no-color" in sys.argv and "--force-color" not in sys.argv:
            os.environ["NO_COLOR"] = "1"
            color_system = None
        elif '--force-color' in sys.argv:
            os.environ["FORCE_COLOR"] = "1"
            force_terminal = True

        from typer import main

        main.console_stderr = Console(
            stderr=True,
            force_terminal=force_terminal,
            color_system=color_system
        )

        # This monkey patch is required because typer does
        # not expose a good way to custom configure the Console objects
        # it uses - revisit this if/when typer exposes control of the
        # console object.
        from typer import rich_utils
        console_getter = rich_utils._get_rich_console
        def get_console():
            console = console_getter()
            ctx = get_current_context(silent=True)
            cmd = get_current_command()
            console.no_color = (
                ctx.params.get('no_color', 'NO_COLOR' in os.environ)
                if ctx else
                (cmd.no_color if cmd else 'NO_COLOR' in os.environ)
            )
            if console.no_color:
                # also remove highlights so there are
                # no ansi control characters in the text
                console._color_system = None
            elif cmd and cmd.force_color:
                console._color_system = 'auto'
                console._force_terminal = True
            return console
        rich_utils._get_rich_console = get_console
    except ImportError:
        pass
    except:
        # not critical code - no reason to tank the library
        pass
