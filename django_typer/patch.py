"""
Stuffing the typer interface into the Django BaseCommand_ interface is an exercise
in fitting a square peg into a round hole. A small amount of upstream patching is
required to make this work. All monkey patching is defined in this module to more
easily keep track of it.

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
import typing as t

import click

from django_typer.utils import get_current_command

PATCH_APPLIED = False

# DO NOT IMPORT ANYTHING FROM TYPER HERE


def apply() -> None:
    """
    Apply monkey patches to get our console objects to recognize django's --no-color
    and --force-color options.
    """
    global PATCH_APPLIED
    if PATCH_APPLIED:
        return
    PATCH_APPLIED = True

    try:
        # Django as of <=5.0 calls colorama.init() if colorama is installed
        # this screws up forced terminals on platforms other than windows that
        # are not attached to ttys. Upstream Django should change the init
        # call to a just_fix_windows_console - we undo this and redo the right
        # thing here.
        import colorama

        colorama.deinit()
        colorama.just_fix_windows_console()
    except ImportError:
        pass

    try:
        from rich.console import Console

        # this has to go here before rich Consoles are instantiated by Typer
        color_system: t.Optional[
            t.Literal["auto", "standard", "256", "truecolor", "windows"]
        ] = "auto"
        force_terminal: t.Optional[bool] = None
        if "--no-color" in sys.argv and "--force-color" not in sys.argv:
            os.environ["NO_COLOR"] = "1"
            color_system = None
        elif "--force-color" in sys.argv:
            os.environ["FORCE_COLOR"] = "1"
            force_terminal = True

        from typer import main

        main.console_stderr = Console(
            stderr=True, force_terminal=force_terminal, color_system=color_system
        )

        # This monkey patch is required because typer does
        # not expose a good way to custom configure the Console objects
        # it uses - revisit this if/when typer exposes control of the
        # console object.
        from typer import rich_utils

        console_getter = rich_utils._get_rich_console

        def get_console(stderr: bool = False) -> Console:
            """
            Tweak the internals of the Console created by typer to match
            our context or command.

            Of all the patching this is the sketchiest.
            """
            console = console_getter(stderr=stderr)
            ctx = click.get_current_context(silent=True)
            cmd = get_current_command()
            console.no_color = (
                ctx.params.get("no_color", "NO_COLOR" in os.environ)
                if ctx
                else (cmd.no_color if cmd else "NO_COLOR" in os.environ)
            )
            console._file = (
                (cmd.stderr if stderr else cmd.stdout) if cmd else console._file
            )
            if console.no_color:
                # also remove highlights so there are
                # no ansi control characters in the text
                console._color_system = None
            elif cmd and cmd.force_color:
                console._force_terminal = True  # set this before detect color!
                console._color_system = console._detect_color_system()
            return console

        rich_utils._get_rich_console = get_console
    except ImportError:
        pass

    # this is a patch to fix lazy translation failure in some circumstances
    # when Argument helps are gettext_lazy proxies. This is I think actually
    # a problem with typer that can be fixed in a number of different ways
    # but this is the easiest
    from click import _compat

    strip_ansi = _compat.strip_ansi
    _compat.strip_ansi = lambda value: strip_ansi(str(value))


from typer import __version__ as typer_version

if (0, 4, 0) <= tuple(int(v) for v in typer_version.split(".")) <= (0, 9, 0):
    from typer import main as typer_main
    from typer.models import ParamMeta

    upstream_get_click_param = typer_main.get_click_param

    def patched_get_click_param(
        param: ParamMeta,
    ) -> t.Tuple[t.Union[click.Argument, click.Option], t.Any]:
        """
        Patch this bug: https://github.com/tiangolo/typer/issues/334

        This gets shell completions working for arguments. As of 0.9.0 I have
        an open PR to fix this problem upstream, but it is enough of an issue
        that its worth patching here until it gets merged.
        """
        click_param = upstream_get_click_param(param)
        if isinstance(click_param[0], click.Argument) and getattr(
            param.default, "shell_complete", None
        ):
            click_param[0]._custom_shell_complete = param.default.shell_complete
        return click_param

    typer_main.get_click_param = patched_get_click_param
else:  # pragma: no cover
    pass
