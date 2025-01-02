import subprocess
from pathlib import Path

from click.shell_completion import CompletionItem
from django.utils.translation import gettext as _

from ..shellcompletion import DjangoTyperShellCompleter


class PowerShellComplete(DjangoTyperShellCompleter):
    name = "powershell"
    template = "shell_complete/powershell.ps1"

    def format_completion(self, item: CompletionItem) -> str:
        return f"{item.value}:::{item.help or ' '}"

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
                except UnicodeDecodeError:
                    pass
        raise RuntimeError(_("Unable to find the PowerShell user profile."))

    def install(self) -> Path:
        assert self.prog_name
        self.uninstall()
        self.set_execution_policy()
        profile = self.get_user_profile()
        profile.parent.mkdir(parents=True, exist_ok=True)
        with profile.open(mode="a") as f:
            f.writelines([self.source()])
        return profile

    def uninstall(self):
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
    name = "pwsh"
