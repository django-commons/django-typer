.. include:: ./refs.rst

.. _extensions:

============================
Tutorial: Extending Commands
============================

You may need to change the behavior of an
`upstream command <https://en.wikipedia.org/wiki/Upstream_(software_development)>`_ or wish
you could add an additional subcommand or group to it. django-typer_ offers two patterns for
changing or extending the behavior of commands. :class:`~django_typer.TyperCommand` classes
support inheritance, even multiple inheritance. This can be a way to override or add additional
commands to a command implemented elsewhere. You can then use Django's built in command override
precedence (INSTALLED_APPS) to ensure your command is used instead of the upstream command or
give it a different name if you would like the upstream command to still be available. The second
pattern allows commands and groups to be added or overridden directly on upstream commands without
inheritance. This mechanism is useful when you might expect other apps, perhaps even unknown apps
to also modify the original command.

For this tutorial, let's consider the task of backing up a Django website. State is stored in the
database, in media files on disk, potentially in other files, and also in the software stack
running on the server. If we want to provide a general backup command that might be used
downstream we cannot know all potential state that might need backing up. Lets use django-typer_
to define a command that can be extended with additional backup routines. On our base command we'll
just provide a database backup routine, but we anticipate our command being extended so lets also
provide default behavior that will run every backup routine defined on the command. We can use the
click_ context to resolve these subroutines at runtime. Our command might look like this:


.. literalinclude:: ../../django_typer/examples/tutorial/backup/backup.py
   :language: python
   :caption: Base Backup Command
   :linenos:

.. typer:: django_typer.examples.tutorial.backup.backup.Command:typer_app
    :prog: manage.py backup
    :width: 80
    :show-nested:
    :convert-png: latex
    :theme: dark


Inheritance
-----------

The first option we have is simple inheritance. Lets say the base command is defined in
an app called backup. Now say we have another app that adds functionality that uses media
files to our site. This means we'll want to add a media backup routine to the backup command.

Say our app tree looks like this:

.. code-block:: text

    site/
    ├── backup/
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── management/
    │   │   ├── __init__.py
    │   │   └── commands/
    │   │       ├── __init__.py
    │   │       └── backup.py
    └── media/
        ├── __init__.py
        ├── apps.py
        └── management/
            ├── __init__.py
            └── commands/
                ├── __init__.py
                └── backup.py

.. code-block:: python

    INSTALLED_APPS = [
        'media',
        'backup',
        ...
    ]

Our backup.py implementation in the media app might look like this:

.. literalinclude:: ../../django_typer/examples/tutorial/backup/backup_inherit.py
   :language: python
   :caption: Media Backup Extension
   :replace:
        django_typer.tests.apps.backup : site.media



Without Overriding
~~~~~~~~~~~~~~~~~~

If you do not wish to override the command you may inherit from it and place it in a module
of a different name. Now you'll have a command with your adjustments that may be called
separately.



Adding to Existing Commands
---------------------------

