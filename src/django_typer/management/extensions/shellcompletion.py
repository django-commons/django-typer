from django_typer.shells import register_completion_class
from django_typer.shells.bash import BashComplete
from django_typer.shells.fish import FishComplete
from django_typer.shells.powershell import (
    PowerShellComplete,
    PwshComplete,
)
from django_typer.shells.zsh import ZshComplete

register_completion_class(ZshComplete)
register_completion_class(BashComplete)
register_completion_class(PowerShellComplete)
register_completion_class(PwshComplete)
register_completion_class(FishComplete)
