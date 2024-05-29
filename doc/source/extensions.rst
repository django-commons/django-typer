.. include:: ./refs.rst

.. _extensions:

============================
Tutorial: Extending Commands
============================

You may need to change the behavior of an
`upstream command <https://en.wikipedia.org/wiki/Upstream_(software_development)>`_ or wish
you could add an additional subcommand or group to it. django-typer_ offers two patterns for
changing or extending the behavior of commands. :class:`~django_typer.TyperCommand` classes
:ref:`support inheritance <inheritance>`, even multiple inheritance. This can be a way to override
or add additional commands to a command implemented elsewhere. You can then use Django's built in
command override precedence (INSTALLED_APPS) to ensure your command is used instead of the upstream
command or give it a different name if you would like the upstream command to still be available.
The :ref:`plugin pattern <plugin>` allows commands and groups to be added or overridden
directly on upstream commands without inheritance. This mechanism is useful when you might expect
other apps to also modify the original command. Conflicts are resolved in INSTALLED_APPS order.

Consider the task of backing up a Django website. State is stored in the database, in media files
on disk, potentially in other files, and also in the software stack running on the server. If we
want to provide a general backup command that might be used downstream we cannot know all potential
state that might need backing up. We can use django-typer_ to define a command that can be extended
with additional backup logic. On our base command we'll only provide a database backup routine,
but we anticipate our command being extended so we may also provide default behavior that will
discover and run every backup routine defined on the command if no specific subroutine is invoked.
We can `use the context <https://typer.tiangolo.com/tutorial/commands/context/#getting-the-context>`_
to determine if a subcommand was called in our root initializer callback and we can find
subroutines added by extensions at runtime using :func:`~django_typer.TyperCommand.get_subcommand`.
Our command might look like this:


.. literalinclude:: ../../django_typer/tests/apps/examples/extensions/backup/management/commands/backup.py
   :language: python
   :caption: Base Backup Command
   :linenos:

.. typer:: django_typer.tests.apps.examples.extensions.backup.management.commands.backup.Command:typer_app
    :prog: manage.py backup
    :width: 80
    :show-nested:
    :convert-png: latex
    :theme: dark

|

.. _inheritance:

Inheritance
-----------

The first option we have is simple inheritance. Lets say the base command is defined in
an app called backup. Now say we have another app that adds functionality that uses media
files to our site. This means we'll want to add a media backup routine to the backup command.

.. note::

    Inheritance also works for commands defined using the Typer-style function based interface.
    Just import Command from the upstream command module and subclass it just as you would if you
    had defined it using the class based interface.

Say our app tree looks like this:

.. code-block:: text

    ./
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

.. literalinclude:: ../../django_typer/tests/apps/examples/extensions/media1/management/commands/backup.py
   :language: python
   :caption: Media Backup Extension
   :replace:
        django_typer.tests.apps.examples.extensions.backup : media

Now you'll see we have another command called media available:

.. typer:: django_typer.tests.apps.examples.extensions.media1.management.commands.backup.Command:typer_app
    :prog: manage.py backup
    :width: 80
    :convert-png: latex
    :theme: dark

|

Now we have a media backup routine that we can run individually or part of the entire
backup batch:

.. typer:: django_typer.tests.apps.examples.extensions.media1.management.commands.backup.Command:typer_app:media
    :prog: manage.py backup media
    :width: 80
    :convert-png: latex
    :theme: dark


.. code-block:: bash

    # backup media only
    $ python manage.py backup media
    # or backup database and media
    $ python manage.py backup

.. warning::

    Inheritance is not supported from typical Django commands that used argparse to define their
    interface.


When Does Inheritance Make Sense?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Inheritance is a good choice when you want to tweak the behavior of a specific command and do not
expect other apps to also modify the same command. It's also a good choice when you want to offer
a different flavor of a command under a different name.

What if other apps want to alter the same command and we don't know about them, but they may end up
installed along with our app? This is where the plugin pattern will serve us better.


.. _plugin:

Plugins
-----------

**The plugin pattern allows us to add or override commands and groups on an upstream command
directly without overriding it or changing its name. This allows downstream apps that know
nothing about each other to add their own behavior to the same command. If there are conflicts
they are resolved in INSTALLED_APPS order.**

To do this we have to abandon the class based interface and place our extensions in a module other
than ``commands``. Let us suppose we are developing a site that uses the backup and media app from
upstream and we've implemented most of our custom site functionality in a new app called my_app.
Because we're now mostly working at the level of our particular site we may want to add more custom
backup logic. For instance, lets say we know our site will always run on sqlite and we prefer
to just copy the file to backup our database. Lets also pretend that it is useful for us to backup
the python stack (e.g. requirements.txt) running on our server. To do that we can use the
plugin pattern to add our environment backup routine and override the database routine from
the upstream backup app. Our app tree now might look like this:

.. code-block:: text

    ./
    ├── backup/
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── management/
    │   │   ├── __init__.py
    │   │   └── commands/
    │   │       ├── __init__.py
    │   │       └── backup.py
    ├── media/
    │   ├── __init__.py
    │   ├── apps.py
    │   └── management/
    │       ├── __init__.py
    │       ├── commands/
    │       └── extensions/
    │           └── __init__.py
    │           └── backup.py
    └── my_app/
        ├── __init__.py
        ├── apps.py
        └── management/
            ├── __init__.py
            ├── commands/
            └── extensions/
                └── __init__.py
                └── backup.py


Note that we've added an ``extensions`` directory to the management directory of the media and
my_app apps. This is where we'll place our extension commands. There is an additional step we must
take. In the ``apps.py`` file of the media and my_app apps we must register our extensions like
this:

.. code-block:: python

    from django.apps import AppConfig
    from django_typer.utils import register_command_extensions

    class MyAppConfig(AppConfig):
        name = 'my_app'

        def ready(self):
            from .management import extensions

            register_command_extensions(extensions)

.. note::

    Because we explicitly register our extensions we can call the package whatever we want.
    django-typer does not require it to be named ``extensions``. It is also important to
    do this inside ready() because conflicts are resolved in the order in which the extension
    modules are registered and ready() methods are called in INSTALLED_APPS order.

For plugins to work, we'll need to re-mplement media from above as a composed extension
and that would look like this:

.. literalinclude:: ../../django_typer/tests/apps/examples/extensions/media2/management/extensions/backup.py
   :language: python
   :caption: Media Backup Extension
   :replace:
        django_typer.tests.apps.examples.extensions.backup : backup

And our my_app extension might look like this:

.. literalinclude:: ../../django_typer/tests/apps/examples/extensions/my_app/management/extensions/backup.py
   :language: python
   :caption: MyApp Backup Extension
   :replace:
        django_typer.tests.apps.examples.extensions.backup : backup

Note that we now have a new environment command available:

.. typer:: backup_example:app
    :prog: manage.py backup
    :width: 80
    :convert-png: latex
    :theme: dark

.. typer:: backup_example:app:environment
    :prog: manage.py backup environment
    :width: 80
    :convert-png: latex
    :theme: dark

|

And the command line parameters to database have been removed:

.. typer:: backup_example:app:database
    :prog: manage.py backup database
    :width: 80
    :convert-png: latex
    :theme: dark

|

.. note::

    The extension code is lazily loaded. This means extensions are resolved on command classes
    the first time an instance of the class is instantiated. This avoids unnecessary code
    execution but does mean that if you are working directly with the ``typer_app`` attribute
    on a :class:`~django_typer.TyperCommand` you will need to make sure at least one instance
    has been instantiated.


Overriding Groups
~~~~~~~~~~~~~~~~~

Some commands might have deep nesting of subcommands and groups. If you want to override a
group or subcommand of a group down a chain of commands you simply need to access the
:class:`~django_typer.CommandGroup` instance of the group you want to override or extend:

.. code-block:: python

    from somewhere.upstream.management.commands.command import Command

    # add a command to grp2 which is a subgroup of grp1
    @Command.grp1.grp2.command()
    def my_command():  # remember self is optional
        pass

    # add a subgroup to grp2 which is a subgroup of grp1
    @Command.grp1.grp2.group()
    def grp3():
        pass

You may even override the initializer of a predefined group:

.. code-block:: python

    from somewhere.upstream.management.commands.command import Command

    # override the initializer (typer callback) of grp1 on Command,
    # this will not alter the child groups of grp1 (grp2, grp3, etc.)
    @Command.grp1.initialize()
    def grp1_init(self):
        pass

    @Command.group()
    def grp1(self):
        """
        This would override grp1 entirely and remove all subcommands
        and groups.
        """

When Do Plugins Make Sense?
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Plugins can be used to group like behavior together under a common root command. This can be
thought of as a way to namespace CLI tools or easily share significant code between tools that have
common initialization logic. Moreover it allows you to do this safely and in a way that can be
deterministically controlled in settings. Most use cases are not this complex and even our backup
example could probably better be implemented as a batch of commands.

Django apps are great for forcing separation of concerns on your code base. In large self contained
projects its often a good idea to break your code into apps that are as self contained as possible.
Plugins can be a good way to organize commands in a code base that follows this pattern. It
also allows for deployments that install a subset of those apps and is therefore a good way to
organize commands in code bases that serve as a framework for a particular kind of site or that
support selecting the features to install.
