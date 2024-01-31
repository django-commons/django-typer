.. include:: ./refs.rst

============
Django Typer
============

Use Typer to define the CLI for your Django management commands. Provides a TyperCommand class that
inherits from django.core.management.BaseCommand and allows typer-style annotated function handlers.
All of the BaseCommand functionality is preserved, so that TyperCommand can be a drop in replacement.

.. warning::

    This is a late beta release. The interface is mostly stable but there may be lingering issues.


.. code-block:: python

    from django_typer import TyperCommand


    class Command(TyperCommand):
        
        help = 'A command that uses Typer'

        def handle(self, arg1: str, arg2: str, arg3: float = 0.5, arg4: int = 1):
            ...


Installation
------------

1. Clone django-typer from GitHub_ or install a release off PyPI_ :

.. code:: bash

       pip install django-typer


2. Add ``django_typer`` to your ``INSTALLED_APPS`` setting:

.. code:: python

       INSTALLED_APPS = [
           ...
           'django_typer',
       ]


.. toctree::
   :maxdepth: 2
   :caption: Contents:

   commands
   reference
   changelog
