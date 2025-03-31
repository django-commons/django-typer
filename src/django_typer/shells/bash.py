import typing as t
from functools import cached_property
from pathlib import Path

from click.shell_completion import CompletionItem

from . import DjangoTyperShellCompleter


class BashComplete(DjangoTyperShellCompleter):
    """
    This completer class supports the bash_ shell. Completion scripts are
    installed in the ``~/.bash_completions`` directory and are sourced in
    ``~/.bashrc``.

    Bash_ does not support help text in completions so these are not returned.
    The format of the completion is ``type,value`` and different suggestions
    are separated by newlines.

    See also: https://github.com/scop/bash-completion#faq
    """

    name = "bash"
    """
    shell executable.
    """

    template = "shell_complete/bash.sh"
    """
    The template used to render the bash completion script.
    """

    supports_scripts = True
    """
    The bash completer supports script invocations.
    """

    color = False
    """
    Zsh_ does support ansi control codes in completion suggestions, but we disable them
    by default.
    """

    def get_user_profile(self) -> Path:
        """
        Get .bashrc it is always located in the user's home directory.
        """
        return Path.home() / ".bashrc"

    @cached_property
    def install_dir(self) -> Path:
        install_dir = self.get_user_profile().parent / ".bash_completions"
        install_dir.mkdir(parents=True, exist_ok=True)
        return install_dir

    @staticmethod
    def _check_version() -> t.Optional[t.Tuple[int, int]]:
        import re
        import subprocess

        output = subprocess.run(
            ["bash", "-c", 'echo "${BASH_VERSION}"'], stdout=subprocess.PIPE
        )
        match = re.search(r"^(\d+)\.(\d+)\.\d+", output.stdout.decode())
        return (int(match.groups()[0]), int(match.groups()[1])) if match else None

    def source_vars(self) -> t.Dict[str, t.Any]:
        """
        When the bash version is 4.4 or higher, the ``nosort`` option is
        available and can be used to disable sorting of completions. We
        add an additional context variable to the template to include this:

        * ``complete_opts``: The options to pass to bash's ``complete`` command.
        """
        complete_opts = ""
        version = self._check_version()
        if version and version >= (4, 4):
            complete_opts = "-o nosort"
        return {
            **super().source_vars(),
            "complete_opts": complete_opts,
            "bash_version": version,
            "use_compopt": version and version >= (4, 4),
        }

    def format_completion(self, item: CompletionItem) -> str:
        return f"{item.type},{item.value}"

    def install(self, prompt: bool = True) -> t.List[Path]:
        assert self.prog_name
        edited = []
        script = self.install_dir / f"{self.prog_name}.sh"
        bashrc = self.get_user_profile()
        bashrc_source = bashrc.read_text() if bashrc.is_file() else ""
        source_line = f"source {script}"
        if source_line not in bashrc_source:
            bashrc_source += f"\n{source_line}\n"
            if self.prompt(
                prompt=prompt,
                source=source_line,
                file=bashrc,
                start_line=bashrc_source.count("\n") + 1,
            ):
                Path.home().mkdir(parents=True, exist_ok=True)
                with open(bashrc, "a") as f:
                    f.write(f"\n{source_line}\n")
                edited.append(bashrc)

        source = self.source()
        if self.prompt(prompt=prompt, source=source, file=script):
            script.parent.mkdir(parents=True, exist_ok=True)
            script.write_text(self.source())
            edited.append(script)
        return edited

    def uninstall(self):
        assert self.prog_name
        script = self.install_dir / f"{self.prog_name}.sh"
        if script.is_file():
            script.unlink()

        bashrc = self.get_user_profile()
        if bashrc.is_file():
            bashrc_source = bashrc.read_text()
            bashrc.write_text(bashrc_source.replace(f"source {script}\n", ""))
