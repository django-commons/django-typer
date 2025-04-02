import subprocess
import typing as t
from pathlib import Path

from click.shell_completion import CompletionItem

from . import DjangoTyperShellCompleter


class PowerShellComplete(DjangoTyperShellCompleter):
    """
    This completer class supports the PowerShell_ versions < 6.
    See :class:`~PwshComplete` for versions >= 6.

    Completion scripts are installed into the user's profile file.

    Returned suggestions are delimited by ``:::``. Each suggestion is one one line.
    """

    name = "powershell"
    """
    shell executable.
    """

    template = "shell_complete/powershell.ps1"
    """
    The template used to render the powershell completion script.
    """

    supports_scripts = False
    """
    PowerShell does not support script invocations.
    """

    color = False
    """
    PowerShell_ does support ansi control codes in completion suggestions, but we
    disable them by default.
    """

    def format_completion(self, item: CompletionItem) -> str:
        return ":::".join(
            [
                item.type,
                self.process_rich_text(item.value),
                " ".join(
                    [
                        ln.strip()
                        for ln in self.process_rich_text(item.help or " ").splitlines()
                    ]
                ),
            ]
        )

    def set_execution_policy(self) -> None:
        subprocess.run(
            [
                self.name,
                "-Command",
                "Set-ExecutionPolicy",
                "Unrestricted",
                "-Scope",
                "CurrentUser",
            ]
        )

    def get_user_profile(self) -> Path:
        result = subprocess.run(
            [self.name, "-NoProfile", "-Command", "echo", "$profile"],
            check=True,
            stdout=subprocess.PIPE,
        )
        if result.returncode == 0:
            for encoding in ["windows-1252", "utf8", "cp850"]:
                try:
                    return Path(result.stdout.decode(encoding).strip())
                except UnicodeDecodeError:  # pragma: no cover
                    pass
        raise RuntimeError(
            "Unable to find the PowerShell user profile."
        )  # pragma: no cover

    def install(self, prompt: bool = True) -> t.List[Path]:
        assert self.prog_name
        self.uninstall()
        self.set_execution_policy()
        profile = self.get_user_profile()
        start_line = 0 if not profile.exists() else profile.read_text().count("\n") + 1
        source = self.source()
        if self.prompt(
            prompt=prompt, source=source, file=profile, start_line=start_line
        ):
            profile.parent.mkdir(parents=True, exist_ok=True)
            with profile.open(mode="a") as f:
                f.writelines(["", self.source()])
            return [profile]
        return []

    def uninstall(self) -> None:
        # annoyingly, powershell has one profile script for all completion commands
        # so we have to find our entry and remove it
        assert self.prog_name
        self.set_execution_policy()
        profile = self.get_user_profile()
        if not profile.exists():
            return
        edited_lines = []
        mark = None
        with open(profile, "rt", encoding="utf-8") as pwr_sh:
            for line in pwr_sh.readlines():
                edited_lines.append(line)
                if line.startswith("Import-Module PSReadLine"):
                    mark = len(edited_lines) - 1
                elif (
                    mark is not None
                    and line.startswith("Register-ArgumentCompleter")
                    and f" {self.command.manage_script_name} " in line
                ):
                    edited_lines = edited_lines[:mark]
                    mark = None

        if edited_lines:
            with open(profile, "wt", encoding="utf-8") as pwr_sh:
                pwr_sh.writelines(edited_lines)
        else:
            profile.unlink()


class PwshComplete(PowerShellComplete):
    """
    This completer class supports the PowerShell_ versions >= 6. See
    :class:`~PowerShellComplete` for versions < 6.

    All behaviors are the same as :class:`~PowerShellComplete`, except that ``pwsh`` is
    used instead of ``powershell``.
    """

    name = "pwsh"
    """
    shell executable.
    """
