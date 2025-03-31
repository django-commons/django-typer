import os
import typing as t
from functools import cached_property
from pathlib import Path

from click.shell_completion import CompletionItem

from . import DjangoTyperShellCompleter


class FishComplete(DjangoTyperShellCompleter):
    """
    This completer class supports the fish_ shell. Completion scripts are installed in
    the ``~/.config/fish/completions`` directory.

    Returned suggestions are formatted as ``type,value[\thelp]``. Each suggestion is on
    one line and if no help is provided, the help text including the tab delimiter is
    omitted.
    """

    name = "fish"
    """
    shell executable.
    """

    template = "shell_complete/fish.fish"
    """
    The template used to render the fish completion script.
    """

    supports_scripts = False
    """
    Fish does not support script invocations.
    """

    color = False
    """
    Fish does not support ansi control codes.
    """

    def get_user_profile(self) -> Path:
        """
        Get the user's fish config file. It is located in the user's home directory by
        default unless the ``XDG_CONFIG_HOME`` environment variable is set.
        """
        return (
            Path(os.environ.get("XDG_CONFIG_HOME", Path.home() / ".config"))
            / "fish/config.fish"
        )

    @cached_property
    def install_dir(self) -> Path:
        install_dir = self.get_user_profile().parent / "completions"
        install_dir.mkdir(parents=True, exist_ok=True)
        return install_dir

    def format_completion(self, item: CompletionItem) -> str:
        if item.help:
            return (
                f"{item.type},{self.process_rich_text(item.value)}\t"
                f"{self.process_rich_text(item.help)}"
            )
        return f"{item.type},{self.process_rich_text(item.value)}"

    def install(self, prompt: bool = True) -> t.List[Path]:
        assert self.prog_name
        script = self.install_dir / f"{self.prog_name}.fish"
        source = self.source()
        if self.prompt(prompt=prompt, source=source, file=script):
            script.write_text(source)
            return [script]
        return []

    def uninstall(self):
        assert self.prog_name
        script = self.install_dir / f"{self.prog_name}.fish"
        if script.is_file():
            script.unlink()
