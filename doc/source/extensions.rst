.. include:: ./refs.rst

.. _extensions:

============================
Tutorial: Extending Commands
============================

There are two supported patterns for extending commands. Each has their place, and we will use
the example of a backup command to illustrate the difference between these patterns. The job of
our backup command is to group together (namespace) all of the business logic necessary to backup
our website. We would like there to be individual

* Class Inheritance
    TyperCommands may inherit, extend and override parts of upstream TyperCommand classes.
* Adding to Existing Commands
    You may use django-typer to add additional command groups and subcommands to commands defined
    in other Django apps.


Inheritance
-----------

Say we have a command called backup in app1 and we want to tweak how it does its work. To
override it in app2, we create a module of the same name and place app2 above app1 in our
INSTALLED_APPS setting:

.. code-block:: text

    site/
    ├── app1/
    │   ├── __init__.py
    │   ├── apps.py
    │   ├── management/
    │   │   ├── __init__.py
    │   │   └── commands/
    │   │       ├── __init__.py
    │   │       └── backup.py
    └── app2/
        ├── __init__.py
        ├── apps.py
        └── management/
            ├── __init__.py
            └── commands/
                ├── __init__.py
                └── backup.py

.. code-block:: python

    INSTALLED_APPS = [
        'app2',
        'app1',
        ...
    ]

Say backup.py in app1 looks like this:

.. code-block:: python

    # todo



Without Overriding
~~~~~~~~~~~~~~~~~~

If you do not wish to override the command you may inherit from it and place it in a module
of a different name. Now you'll have a command with your adjustments that may be called
separately.



Adding to Existing Commands
---------------------------

