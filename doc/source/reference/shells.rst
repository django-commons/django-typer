.. include:: ../refs.rst

.. _shells:

======
Shells
======

.. autoclass:: django_typer.shells.bash.BashComplete
    :members: name, template, color, supports_scripts

.. autoclass:: django_typer.shells.zsh.ZshComplete
    :members: name, template, color, supports_scripts

.. autoclass:: django_typer.shells.powershell.PowerShellComplete
    :members: name, template, color, supports_scripts

.. autoclass:: django_typer.shells.powershell.PwshComplete
    :members: name, template, color, supports_scripts

.. autoclass:: django_typer.shells.fish.FishComplete
    :members: name, template, color, supports_scripts
