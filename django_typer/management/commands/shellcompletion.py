"""
The shellcompletion command is a Django_ management command that installs and removes
shellcompletion scripts for supported shells (bash, fish, zsh, powershell). This
command is also the entry point for running the completion logic and can be used to
debug completer code.

.. typer:: django_typer.management.commands.shellcompletion.Command:typer_app
    :prog: manage.py shellcompletion
    :width: 80
    :convert-png: latex

:func:`~django_typer.management.commands.shellcompletion.Command.install` invokes typer's shell
completion installation logic, but does have to patch the installed scripts. This is because
there is only one installation for all Django_ management commands, not each individual command.
The completion logic here will failover to Django_'s builtin autocomplete if the command in
question is not a :class:`~django_typer.TyperCommand`. To promote compatibility with other
management command libraries or custom completion logic, a fallback completion function can also
be specified.
"""

import collections.abc as cabc
import contextlib
import io
import os
import re
import sys
import typing as t
import warnings
from functools import cached_property
from importlib.resources import files
from pathlib import Path
from types import ModuleType

from click.core import Command as ClickCommand
from click.shell_completion import (
    CompletionItem,
    ShellComplete,
    add_completion_class,
    split_arg_string,
)
from django.core.management import CommandError, ManagementUtility
from django.template import Context, Engine
from django.utils.functional import classproperty
from django.utils.module_loading import import_string
from django.utils.translation import gettext
from django.utils.translation import gettext_lazy as _
from shellingham import ShellDetectionFailure, detect_shell
from typer import Argument, Option
from typer.main import get_command as get_typer_command

from django_typer.completers import these_strings
from django_typer.management import TyperCommand, command, get_command, initialize
from django_typer.types import COMMON_PANEL
from django_typer.utils import get_usage_script

DETECTED_SHELL = None

try:
    DETECTED_SHELL = detect_shell()[0]
except (ShellDetectionFailure, RuntimeError):
    pass


class DjangoTyperShellCompleter(ShellComplete):
    """
    An extension to the click shell completion classes that provides a Django specific
    shell completion implementation. If you wish to support a new shell, you must
    derive from this class, implement all of the abstract methods, and register the
    class with
    :func:`~django_typer.management.commands.shellcompletion.register_completion_class`
    """

    SCRIPT: Path
    """
    The path to the shell completion script template.
    """

    color: bool = False
    """
    By default, allow or disallow color in the completion output.
    """

    supports_scripts: bool = False
    """
    Does the shell support completions for uninstalled scripts? (i.e. not on the path)
    """

    complete_var: str = ""

    command: "Command"
    command_str: str
    command_args: t.List[str]

    def __init__(
        self,
        cli: t.Optional[ClickCommand] = None,
        ctx_args: cabc.MutableMapping[str, t.Any] = {},
        prog_name: str = "",
        complete_var: str = "",
        command: t.Optional["Command"] = None,
        command_str: t.Optional[str] = None,
        command_args: t.Optional[t.List[str]] = None,
        **kwargs,
    ):
        # we don't always need the initialization parameters during completion
        self.prog_name = kwargs.pop("prog_name", "")
        if command:
            self.command = command
        if command_str is not None:
            self.command_str = command_str
        if command_args is not None:
            self.command_args = split_arg_string(command_str) if command_str else []

        if cli:
            super().__init__(
                cli=cli,
                ctx_args=ctx_args,
                complete_var=complete_var,
                prog_name=prog_name,
                **kwargs,
            )

    @classproperty
    def source_template(self) -> str:  # type: ignore
        return self.SCRIPT.read_text()

    def get_completions(
        self, args: t.List[str], incomplete: str
    ) -> t.List[CompletionItem]:
        """
        need to remove the django command name from the arg completions
        """
        if self.command.fallback:
            return self.command.fallback(args, incomplete)
        return super().get_completions(args[1:], incomplete)

    def get_completion_args(self) -> t.Tuple[t.List[str], str]:
        cwords = self.command_args
        if self.command_str and self.command_str[-1].isspace():
            cwords.append("")
        # allow users to not specify the manage script, but allow for it
        # if they do by lopping it off - same behavior as upstream classes
        if cwords:
            try:
                if cwords[0] == self.command.manage_script_name:
                    cwords = cwords[1:]
                elif Path(cwords[0]).resolve() == Path(sys.argv[0]).resolve():
                    cwords = cwords[1:]
            except (TypeError, ValueError, OSError):  # pragma: no cover
                pass
        return (
            cwords[:-1],
            cwords[-1] if cwords else "",
        )

    def source_vars(self) -> t.Dict[str, t.Any]:
        return {
            **super().source_vars(),
            "manage_script": self.command.manage_script,
            "python": sys.executable,
            "django_command": self.command.__module__.split(".")[-1],
            "color": "--no-color"
            if self.command.no_color
            else "--force-color"
            if self.command.force_color
            else "",
            "fallback": f" --fallback {self.command.fallback.__module__}.{self.command.fallback.__name__}"
            if self.command.fallback
            else "",
            "is_installed": not isinstance(self.command.manage_script, Path),
            "rich": "--rich" if self.command.allow_rich else "",
        }

    @cached_property
    def template_engine(self):
        """
        Django template engine that will find and render completer script templates.
        """
        return Engine(
            dirs=[str(files("django_typer.management.commands").joinpath("shells"))],
            libraries={
                "default": "django.template.defaulttags",
                "filter": "django.template.defaultfilters",
            },
        )

    def source(self) -> str:
        """
        Render the completion script template to a string.
        """
        return self.template_engine.get_template(str(self.SCRIPT)).render(
            Context(self.source_vars())
        )

    def install(self):
        raise NotImplementedError

    def uninstall(self):
        raise NotImplementedError


_completers: t.Dict[str, t.Type[DjangoTyperShellCompleter]] = {}


def register_completion_class(cls: t.Type[DjangoTyperShellCompleter]) -> None:
    """
    Register a shell completion class for use with the Django shellcompletion command.
    """
    _completers[cls.name] = cls
    add_completion_class(cls)


def django_autocomplete(args: t.List[str], incomplete: str) -> t.List[CompletionItem]:
    # spoof bash environment variables
    # the first one is lopped off, so we insert a placeholder 0
    args = ["0", *args]
    if args[-1] != incomplete:
        args.append(incomplete)
    else:  # pragma: no cover
        pass
    os.environ["COMP_WORDS"] = " ".join(args)
    os.environ["COMP_CWORD"] = str(args.index(incomplete))
    os.environ["DJANGO_AUTO_COMPLETE"] = "1"
    dj_manager = ManagementUtility(args)
    capture_completions = io.StringIO()
    with contextlib.redirect_stdout(capture_completions):
        try:
            dj_manager.autocomplete()
        except SystemExit:
            pass
    return [
        CompletionItem(item) for item in capture_completions.getvalue().split() if item
    ]


class Command(TyperCommand):
    """
    This command installs autocompletion for the current shell. This command uses the typer/click
    autocompletion scripts to generate the autocompletion items, but monkey patches the scripts
    to invoke our bundled shell complete script which fails over to the django autocomplete
    function when the command being completed is not a :class:`~django_typer.TyperCommand`. When
    the django autocomplete function is used we also wrap it so that it works for any supported
    click/typer shell, not just bash.

    We also provide a remove command to easily remove the installed script.

    Great pains are taken to use the upstream dependency's shell completion logic. This is so
    advances and additional shell support implemented upstream should just work. However, it
    would be possible to add support for new shells here using the pluggable logic that click
    provides. It is probably a better idea however to add support for new shells at the typer
    level.

    Shell autocompletion can be brittle with every shell having its own quirks and nuances. We
    make a good faith effort here to support all the shells that typer/click support, but there
    can easily be system specific configuration issues that prevent this from working. In those
    cases users should refer to the online documentation for their specific shell to troubleshoot.
    """

    help = t.cast(str, _("Install autocompletion for the current shell."))

    # disable the system checks - no reason to run these for this one-off command
    requires_system_checks = []
    requires_migrations_checks = False

    # remove unnecessary django command base parameters - these just clutter the help
    suppressed_base_arguments = {
        "version",
        "skip_checks",
        "verbosity",
    }

    allow_rich: bool = False

    _shell: t.Optional[str] = DETECTED_SHELL
    shell_module: ModuleType

    ANSI_ESCAPE_RE = re.compile(r"\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])")

    _fallback: t.Optional[t.Callable[[t.List[str], str], t.List[CompletionItem]]] = None

    @property
    def fallback(
        self,
    ) -> t.Optional[t.Callable[[t.List[str], str], t.List[CompletionItem]]]:
        return self._fallback

    @fallback.setter
    def fallback(self, fb: t.Optional[str]):
        try:
            self._fallback = import_string(fb) if fb else django_autocomplete
        except ImportError as err:
            raise CommandError(
                gettext("Unable to import fallback completion function: {err}").format(
                    err=str(err)
                )
            ) from err

    @property
    def fallback_import(self) -> t.Optional[str]:
        return (
            f"{self.fallback.__module__}.{self.fallback.__name__}"
            if self.fallback
            else None
        )

    @cached_property
    def manage_script(self) -> t.Union[str, Path]:
        """
        Returns the name of the manage command as a string if it is available as a command
        on the user path. If it is a script that is not available as a command on the path
        it will return an absolute Path object to the script.
        """
        # We do not want to hardcode this as 'manage.py' because users are free to rename and
        # implement their own manage scripts! The safest way to do this is therefore to fetch
        # the name of the script that invoked the shellcompletion command and determine if that
        # script is available on the user's path or not.

        # Most shell's completion infrastructure works best if the commands are available on the
        # path. However, it is common for Django development to be done in a virtual environment
        # with a manage.py script being invoked directly as a script. Completion should work in
        # this case as well, but it does complicate the installation for some shell's so we must
        # first figure out which mode we are in.
        script = get_usage_script()
        if isinstance(script, Path):
            return script.absolute()
        return script

    @cached_property
    def manage_script_name(self) -> str:
        """
        Get the name of the manage script as a command available from the shell's path.
        """
        return str(getattr(self.manage_script, "name", self.manage_script))

    @property
    def shell(self) -> str:
        """
        Get the active shell. If not explicitly set, it first tries to find the shell
        in the environment variable shell complete scripts set and failing that it will try
        to autodetect the shell.
        """
        assert self._shell
        return self._shell

    @shell.setter
    def shell(self, shell: t.Optional[str]):
        """Set the shell to install autocompletion for."""
        if shell:
            self._shell = shell
        if self._shell is None:
            raise CommandError(
                gettext(
                    "Please specify the shell to install or remove "
                    "autocompletion for. Unable to detect shell."
                )
            )

    @property
    def shell_class(self):
        global _completers
        try:
            return _completers[self.shell]
        except KeyError as err:
            raise CommandError(
                gettext("Unsupported shell: {shell}").format(shell=self.shell)
            ) from err

    @initialize()
    def init(
        self,
        shell: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _("The shell to use."),
                ),
                metavar="SHELL",
                shell_complete=these_strings(_completers.keys()),
            ),
        ] = DETECTED_SHELL,
        no_color: t.Annotated[
            t.Optional[bool],
            Option(
                "--no-color",
                help=t.cast(str, _("Filter color codes out of completion text.")),
                rich_help_panel=COMMON_PANEL,
            ),
        ] = None,
        allow_rich: t.Annotated[
            bool,
            Option(
                "--rich", help=t.cast(str, _("Allow rich output in completion text."))
            ),
        ] = allow_rich,
    ) -> "Command":
        self.shell = shell  # type: ignore[assignment]
        assert self.shell
        self.no_color = not self.shell_class.color if no_color is None else no_color
        self.allow_rich = allow_rich
        return self

    @command(
        help=t.cast(str, _("Install autocompletion for the current or given shell."))
    )
    def install(
        self,
        manage_script: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _(
                        "The name of the django manage script to install autocompletion for if "
                        "different than the script used to invoke this command."
                    ),
                )
            ),
        ] = None,
        fallback: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _(
                        "The python import path to a fallback complete function to use when "
                        "the completion command is not a TyperCommand."
                    ),
                )
            ),
        ] = None,
    ):
        """
        Install autocompletion for the given shell. If the shell is not specified, it will
        try to detect the shell. If the shell is not detected, it will fail.

        We run the upstream typer installation routines, with some augmentation.

        .. typer:: django_typer.management.commands.shellcompletion.Command:typer_app:install
            :width: 85
            :convert-png: latex
        """
        self.fallback = fallback  # type: ignore[assignment]
        if (
            isinstance(self.manage_script, Path)
            and not self.shell_class.supports_scripts
        ):
            if not self.shell_class.supports_scripts:
                raise CommandError(
                    gettext(
                        "Shell {shell} does not support autocompletion for scripts that are not "
                        "installed on the path. You must create an entry point for {script_name}. "
                        "See {link}."
                    ).format(
                        shell=self.shell,
                        script_name=self.manage_script_name,
                        link="https://setuptools.pypa.io/en/latest/userguide/entry_point.html",
                    )
                )
            else:
                warnings.warn(
                    gettext(
                        "It is not recommended to install tab completion for a script not on the path."
                    )
                )

        install_path = self.shell_class(
            prog_name=str(manage_script or self.manage_script_name), command=self
        ).install()
        self.stdout.write(
            self.style.SUCCESS(
                gettext("Installed autocompletion for {shell} @ {install_path}").format(
                    shell=self.shell, install_path=install_path
                )
            )
        )

    @command(
        help=t.cast(str, _("Uninstall autocompletion for the current or given shell."))
    )
    def uninstall(
        self,
        manage_script: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _(
                        "The name of the django manage script to remove shell completion for if "
                        "different than the script used to invoke this command."
                    ),
                )
            ),
        ] = None,
    ):
        """
        Remove the autocompletion for the given shell. If the shell is not specified, it will
        try to detect the shell. If the shell is not detected, it will fail.

        Since the installation routine is upstream we first run install to determine where the
        completion script is installed and then we remove it.

        .. typer:: django_typer.management.commands.shellcompletion.Command:typer_app:remove
            :prog: shellcompletion
            :width: 80
            :convert-png: latex

        """
        self.shell_class(
            prog_name=str(manage_script or self.manage_script_name), command=self
        ).uninstall()
        self.stdout.write(
            self.style.WARNING(
                gettext("Uninstalled autocompletion for {shell}.").format(
                    shell=self.shell
                )
            )
        )

    @command(
        help=t.cast(str, _("Generate autocompletion for command string.")), hidden=False
    )
    def complete(
        self,
        command: t.Annotated[
            str,
            Argument(
                help=t.cast(
                    str, _("The command string to generate completion suggestions for.")
                ),
            ),
        ] = "",
        fallback: t.Annotated[
            t.Optional[str],
            Option(
                help=t.cast(
                    str,
                    _(
                        "The python import path to a fallback complete function to use when "
                        "the completion command is not a TyperCommand. By default, the builtin "
                        "django autocomplete function is used."
                    ),
                )
            ),
        ] = None,
    ):
        """
        We implement the shell complete generation script as a Django command because the
        Django environment needs to be bootstrapped for it to work. This also allows
        us to test completion logic in a platform agnostic way.

        .. tip::

            This command is super useful for debugging shell_complete logic. For example to
            enter into the debugger, we could set a breakpoint in our ``shell_complete`` function
            for the option parameter and then run the following command:

            .. code-block:: bash

                $ ./manage.py shellcompletion complete "./manage.py your_command --option "

        .. typer:: django_typer.management.commands.shellcompletion.Command:typer_app:complete
            :prog: shellcompletion
            :width: 80
            :convert-png: latex
        """
        args = split_arg_string(command)

        def get_completion() -> str:
            if args:
                # we first need to figure out which command is being invoked
                # but we cant be sure which index the command name is at so
                # we try to fetch each in order and assume the first arg
                # that resolves to a command is the command
                cmd = None
                cmd_idx = -1
                try:
                    while cmd is None:
                        cmd_idx += 1
                        try:
                            cmd = get_command(args[cmd_idx])
                        except KeyError:
                            pass
                except IndexError:
                    if command.endswith(" "):
                        # unrecognized command
                        return ""
                    # fall through to fallback

                if isinstance(cmd, TyperCommand):
                    # this will exit out so no return is needed here
                    return self.shell_class(
                        cli=get_typer_command(cmd.typer_app),
                        ctx_args={"django_command": cmd},
                        prog_name="",
                        complete_var="",
                        command=self,
                        command_str=command,
                        command_args=args,
                    ).complete()

            # only try to set the fallback if we have to use it
            self.fallback = fallback  # type: ignore[assignment]
            return self.shell_class(
                command=self, command_str=command, command_args=args
            ).complete()

        def strip_color(text: str) -> str:
            """
            Strip ANSI color codes from a string.
            """
            if self.no_color:
                return self.ANSI_ESCAPE_RE.sub("", text)
            return text

        return strip_color(get_completion())


from .shells.bash import BashComplete  # noqa: E402
from .shells.fish import FishComplete  # noqa: E402
from .shells.powershell import PowerShellComplete, PwshComplete  # noqa: E402
from .shells.zsh import ZshComplete  # noqa: E402

register_completion_class(ZshComplete)
register_completion_class(BashComplete)
register_completion_class(PowerShellComplete)
register_completion_class(PwshComplete)
register_completion_class(FishComplete)
