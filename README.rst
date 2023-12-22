|MIT license| |PyPI version fury.io| |PyPI pyversions| |PyPi djversions| |PyPI status| |Documentation Status|
|Code Cov| |Test Status| |Code Style|

.. |MIT license| image:: https://img.shields.io/badge/License-MIT-blue.svg
   :target: https://lbesson.mit-license.org/

.. |PyPI version fury.io| image:: https://badge.fury.io/py/django-typer.svg
   :target: https://pypi.python.org/pypi/django-typer/

.. |PyPI pyversions| image:: https://img.shields.io/pypi/pyversions/django-typer.svg
   :target: https://pypi.python.org/pypi/django-typer/

.. |PyPI djversions| image:: https://img.shields.io/pypi/djversions/django-typer.svg
   :target: https://pypi.org/project/django-typer/

.. |PyPI status| image:: https://img.shields.io/pypi/status/django-typer.svg
   :target: https://pypi.python.org/pypi/django-typer

.. |Documentation Status| image:: https://readthedocs.org/projects/django-typer/badge/?version=latest
   :target: http://django-typer.readthedocs.io/?badge=latest/

.. |Code Cov| image:: https://codecov.io/gh/bckohan/django-typer/branch/main/graph/badge.svg?token=0IZOKN2DYL
   :target: https://codecov.io/gh/bckohan/django-typer

.. |Test Status| image:: https://github.com/bckohan/django-typer/workflows/test/badge.svg
   :target: https://github.com/bckohan/django-typer/actions

.. |Code Style| image:: https://img.shields.io/badge/code%20style-black-000000.svg
   :target: https://github.com/psf/black


django-typer
############

Use Typer to define the CLI for your Django management commands. Provides a TyperCommand class that
inherits from django.core.management.BaseCommand and allows typer-style annotated function handlers.
All of the BaseCommand functionality is preserved, so that TyperCommand can be a drop in replacement.

.. warning::

    This is an early beta release. Expect rapid changes.


.. code-block:: python

    from django_typer import TyperCommand


    class Command(TyperCommand):
        
        help = 'A command that uses Typer'

        def handle(self, arg1: str, arg2: str, arg3: float = 0.5, arg4: int = 1):
            ...

