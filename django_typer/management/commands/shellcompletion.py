import contextlib
import inspect
import io
import os
import subprocess
import sys
import typing as t
from pathlib import Path

from click.parser import split_arg_string
from click.shell_completion import (
    CompletionItem,
    add_completion_class,
    get_completion_class,
)
from django.core.management import CommandError, ManagementUtility
from django.utils.functional import cached_property
from django.utils.module_loading import import_string
from django.utils.translation import gettext_lazy as _
from typer import Argument, Option, echo
from typer.completion import Shells, completion_init

from django_typer import TyperCommand, command, get_command

try:
    from shellingham import detect_shell

    detected_shell = detect_shell()[0]
except Exception:
    detected_shell = None


DJANGO_COMMAND = Path(__file__).name.split(".")[0]


class Command(TyperCommand):
    """
    This command installs autocompletion for the current shell. This command uses the typer/click
    autocompletion scripts to generate the autocompletion items, but monkey patches the scripts
    to invoke our bundled shell complete script which fails over to the django autocomplete function
    when the command being completed is not a TyperCommand. When the django autocomplete function
    is used we also wrap it so that it works for any supported click/typer shell, not just bash.

    We also provide a remove command to easily remove the installed script.

    Great pains are taken to use the upstream dependency's shell completion logic. This is so advances
    and additional shell support implemented upstream should just work. However, it would be possible
    to add support for new shells here using the pluggable logic that click provides. It is
    probably a better idea however to add support for new shells at the typer level.

    Shell autocompletion can be brittle with every shell having its own quirks and nuances. We
    make a good faith effort here to support all the shells that typer/click support, but there
    can easily be system specific configuration issues that prevent this from working. In those
    cases users should refer to the online documentation for their specific shell to troubleshoot.
    """

    help = _("Install autocompletion for the current shell.")

    # disable the system checks - no reason to run these for this one-off command
    requires_system_checks = []
    requires_migrations_checks = False

    # remove unnecessary django command base parameters - these just clutter the help
    django_params = [
        cmd
        for cmd in TyperCommand.django_params
        if cmd not in ["version", "skip_checks", "no_color", "force_color"]
    ]

    _shell: Shells

    COMPLETE_VAR = "_COMPLETE_INSTRUCTION"

    @cached_property
    def manage_script(self) -> t.Union[str, Path]:
        """
        The name of the django manage command script to install autocompletion for. We do
        not want to hardcode this as 'manage.py' because users are free to rename and implement
        their own manage scripts! The safest way to do this is therefore to require this install
        script to be a management command itself and then fetch the name of the script that invoked
        it.

        Get the manage script as either the name of it as a command available from the shell's path if
        it is or as an absolute path to it as a script if it is not a command available on the path. If
        the script is invoked via python, a CommandError is thrown.

        Most shell's completion infrastructure works best if the commands are available on the path.
        However, it is common for Django development to be done in a virtual environment with a manage.py
        script being invoked directly as a script. Completion should work in this case as well, but it
        does complicate the installation for some shell's so we must first figure out which mode we are
        in.
        """
        cmd_pth = Path(sys.argv[0])
        if cmd_pth.resolve() == Path(sys.executable).resolve():
            raise CommandError(
                _(
                    "Unable to install shell completion when invoked via python. It is best to install the "
                    "manage script as a command on your shell's path, but shell completion should also work if "
                    "you invoke the manage script directly."
                )
            )
        if cmd_pth.exists():
            # manage.py might happen to be on the current path, but it might also be installed as
            # a command - we test it here by invoking it to be sure
            try:
                subprocess.run(
                    [cmd_pth.name, "--help"],
                    check=True,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                )
            except Exception:
                return cmd_pth.absolute()
        return cmd_pth.name

    @cached_property
    def manage_script_name(self) -> str:
        """
        Get the name of the manage script as a command available from the shell's path.
        """
        return getattr(self.manage_script, "name", self.manage_script)

    @cached_property
    def manage_command(self):
        if self.manage_installed:
            return sys.argv[0]
        return Path(sys.argv[0]).absolute()

    @property
    def shell(self):
        """
        Get the active shell. If not explicitly set, it first tries to find the shell
        in the environment variable shell complete scripts set and failing that it will try
        to autodetect the shell.
        """
        return getattr(
            self,
            "_shell",
            Shells(
                os.environ[self.COMPLETE_VAR].partition("_")[2]
                if self.COMPLETE_VAR in os.environ
                else detect_shell()[0]
            ),
        )

    @shell.setter
    def shell(self, shell):
        """Set the shell to install autocompletion for."""
        if shell is None:
            raise CommandError(
                _(
                    "Unable to detect shell. Please specify the shell to install or remove "
                    "autocompletion for."
                )
            )
        self._shell = shell if isinstance(shell, Shells) else Shells(shell)

    @cached_property
    def noop_command(self):
        """
        This is a no-op command that is used to bootstrap click Completion classes. It
        has no use other than to avoid any potential attribute errors when we emulate
        upstream completion logic
        """
        return self.get_subcommand("noop")

    def patch_script(
        self, shell: t.Optional[Shells] = None, fallback: t.Optional[str] = None
    ) -> None:
        """
        We have to monkey patch the typer completion scripts to point to our custom
        shell complete script. This is potentially brittle but thats why we have robust
        CI!

        :param shell: The shell to patch the completion script for.
        :param fallback: The python import path to a fallback autocomplete function to use when
            the completion command is not a TyperCommand. Defaults to None, which means the bundled
            complete script will fallback to the django autocomplete function, but wrap it so it works
            for all supported shells other than just bash.
        """
        # do not import this private stuff until we need it - avoids it tanking the whole
        # library if these imports change
        from typer import _completion_shared as typer_scripts

        shell = shell or self.shell

        fallback = f" --fallback {fallback}" if fallback else ""

        def replace(s: str, old: str, new: str, occurrences: list[int]) -> str:
            """
            :param s: The string to modify
            :param old: The string to replace
            :param new: The string to replace with
            :param occurrences: A list of occurrences of the old string to replace with the
                new string, where the occurrence number is the zero-based count of the old
                strings appearance in the string when counting from the front.
            """
            count = 0
            result = ""
            start = 0

            for end in range(len(s)):
                if s[start : end + 1].endswith(old):
                    if count in occurrences:
                        result += f"{s[start:end+1-len(old)]}{new}"
                        start = end + 1
                    else:
                        result += s[start : end + 1]
                        start = end + 1
                    count += 1

            result += s[start:]
            return result

        if shell is Shells.bash:
            typer_scripts._completion_scripts[Shells.bash.value] = replace(
                typer_scripts.COMPLETION_SCRIPT_BASH,
                "$1",
                f"$1 {DJANGO_COMMAND} complete",
                [0],
            )
        elif shell is Shells.zsh:
            typer_scripts._completion_scripts[Shells.zsh.value] = replace(
                typer_scripts.COMPLETION_SCRIPT_ZSH,
                "%(prog_name)s",
                f"${{words[0,1]}} {DJANGO_COMMAND} complete",
                [1],
            )
        elif shell is Shells.fish:
            typer_scripts._completion_scripts[Shells.fish.value] = replace(
                typer_scripts.COMPLETION_SCRIPT_FISH,
                "%(prog_name)s",
                f"{self.manage_script} {DJANGO_COMMAND} complete",
                [1, 2],
            )
        elif shell in [Shells.pwsh, Shells.powershell]:
            script = replace(
                typer_scripts.COMPLETION_SCRIPT_POWER_SHELL,
                "%(prog_name)s",
                f"{self.manage_script} {DJANGO_COMMAND} complete",
                [0],
            )
            typer_scripts._completion_scripts[Shells.powershell.value] = script
            typer_scripts._completion_scripts[Shells.pwsh.value] = script

    @command(help=_("Install autocompletion."))
    def install(
        self,
        shell: t.Annotated[
            t.Optional[Shells],
            Argument(
                help=_("Specify the shell to install or remove autocompletion for.")
            ),
        ] = detected_shell,
        manage_script: t.Annotated[
            t.Optional[str],
            Option(
                help=_(
                    "The name of the django manage script to install autocompletion for if different."
                )
            ),
        ] = None,
        fallback: t.Annotated[
            t.Optional[str],
            Option(
                help=_(
                    "The python import path to a fallback complete function to use when "
                    "the completion command is not a TyperCommand."
                )
            ),
        ] = None,
    ):
        # do not import this private stuff until we need it - avoids tanking the whole
        # library if these imports change
        from typer._completion_shared import install

        self.shell = shell
        self.patch_script(fallback=fallback)
        install_path = install(
            shell=self.shell.value,
            prog_name=manage_script or self.manage_script_name,
            complete_var=self.COMPLETE_VAR,
        )[1]
        self.stdout.write(
            self.style.SUCCESS(
                _("Installed autocompletion for %(shell)s @ %(install_path)s")
                % {"shell": shell.value, "install_path": install_path}
            )
        )

    @command(help=_("Remove autocompletion."))
    def remove(
        self,
        shell: t.Annotated[
            t.Optional[Shells],
            Argument(
                help=_("Specify the shell to install or remove shell completion for.")
            ),
        ] = detected_shell,
        manage_script: t.Annotated[
            t.Optional[str],
            Option(
                help=_(
                    "The name of the django manage script to remove shell completion for if different."
                )
            ),
        ] = None,
    ):
        from typer._completion_shared import install

        # its less brittle to install and use the returned path to uninstall
        self.shell = shell
        stdout = self.stdout
        self.stdout = io.StringIO()
        prog_name = manage_script or self.manage_script_name
        installed_path = install(shell=self.shell.value, prog_name=prog_name)[1]
        if self.shell in [Shells.pwsh, Shells.powershell]:
            # annoyingly, powershell has one profile script for all completion commands
            # so we have to find our entry and remove it
            edited_lines = []
            mark = None
            with open(installed_path, "r") as pwr_sh:
                for line in pwr_sh.readlines():
                    edited_lines.append(line)
                    if line.startswith("Import-Module PSReadLine"):
                        mark = len(edited_lines) - 1
                    elif (
                        mark is not None
                        and line.startswith("Register-ArgumentCompleter")
                        and f" {prog_name} " in line
                    ):
                        edited_lines = edited_lines[:mark]
                        mark = None

            if edited_lines:
                with open(installed_path, "w") as pwr_sh:
                    pwr_sh.writelines(edited_lines)
            else:
                installed_path.unlink()

        else:
            installed_path.unlink()
        self.stdout = stdout
        self.stdout.write(
            self.style.WARNING(
                _("Removed autocompletion for %(shell)s.") % {"shell": shell.value}
            )
        )

    @command(help=_("Generate autocompletion for command string."), hidden=False)
    def complete(
        self,
        command: t.Annotated[
            t.Optional[str],
            Argument(
                help=_("The command string to generate completion suggestions for.")
            ),
        ] = None,
        fallback: t.Annotated[
            t.Optional[str],
            Option(
                help=_(
                    "The python import path to a fallback complete function to use when "
                    "the completion command is not a TyperCommand. By default, the builtin "
                    "django autocomplete function is used."
                )
            ),
        ] = None,
    ):
        """
        We implement the shell complete generation script as a Django command because the
        Django environment needs to be bootstrapped for it to work. This also allows
        us to test autocompletions in a platform agnostic way.
        """
        completion_init()
        CompletionClass = get_completion_class(self.shell.value)
        if command:
            # when the command is given, this is a user testing their autocompletion,
            # so we need to override the completion classes get_completion_args logic
            # because our entry point was not an installed completion script
            def get_completion_args(self) -> t.Tuple[t.List[str], str]:
                cwords = split_arg_string(command)
                # allow users to not specify the manage script, but allow for it
                # if they do by lopping it off - same behavior as upstream classes
                try:
                    if Path(cwords[0]).resolve() == Path(sys.argv[0]).resolve():
                        cwords = cwords[1:]
                except Exception:
                    pass
                return (
                    cwords,
                    cwords[-1] if len(cwords) and not command[-1].isspace() else "",
                )

            CompletionClass.get_completion_args = get_completion_args
            add_completion_class(self.shell.value, CompletionClass)

        args, incomplete = CompletionClass(
            cli=self.noop_command,
            ctx_args=self.noop_command,
            prog_name=sys.argv[0],
            complete_var=self.COMPLETE_VAR,
        ).get_completion_args()

        def call_fallback(fb):
            fallback = import_string(fb) if fb else self.django_fallback
            if command and inspect.signature(fallback).parameters:
                fallback(command)
            else:
                fallback()

        if not args:
            call_fallback(fallback)
        else:
            try:
                os.environ[self.COMPLETE_VAR] = os.environ.get(
                    self.COMPLETE_VAR, f"complete_{self.shell.value}"
                )
                cmd = get_command(args[0])
                if isinstance(cmd, TyperCommand):
                    # invoking the command will trigger the autocompletion?
                    cmd.command_tree.command._main_shell_completion(
                        ctx_args={},
                        prog_name=f"{sys.argv[0]} {cmd.command_tree.command.name}",
                        complete_var=self.COMPLETE_VAR,
                    )
                    return
                else:
                    call_fallback(fallback)
            except Exception as e:
                call_fallback(fallback)

    def django_fallback(self):
        """
        Run django's builtin bash autocomplete function. We wrap the click
        completion class to make it work for all supported shells, not just
        bash.
        """
        CompletionClass = get_completion_class(self.shell.value)

        def get_completions(self, args, incomplete):
            # spoof bash environment variables
            # the first one is lopped off, so we insert a placeholder 0
            args = ["0", *args]
            if args[-1] != incomplete:
                args.append(incomplete)
            os.environ["COMP_WORDS"] = " ".join(args)
            os.environ["COMP_CWORD"] = str(args.index(incomplete))
            os.environ["DJANGO_AUTO_COMPLETE"] = "1"
            dj_manager = ManagementUtility(args)
            capture_completions = io.StringIO()
            try:
                with contextlib.redirect_stdout(capture_completions):
                    dj_manager.autocomplete()
            except SystemExit:
                return [
                    CompletionItem(item)
                    for item in capture_completions.getvalue().split()
                    if item
                ]

        CompletionClass.get_completions = get_completions
        echo(
            CompletionClass(
                cli=self.noop_command,
                ctx_args={},
                prog_name=self.manage_script_name,
                complete_var=self.COMPLETE_VAR,
            ).complete()
        )

    @command(
        hidden=True,
        context_settings={
            "ignore_unknown_options": True,
            "allow_extra_args": True,
            "allow_interspersed_args": True,
        },
    )
    def noop(self):
        """
        This is a no-op command that is used to bootstrap click Completion classes. It
        has no use other than to avoid any potential attribute errors when we spoof
        completion logic
        """
        pass
