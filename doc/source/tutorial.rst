.. include:: ./refs.rst

========
Tutorial
========

Using the :class:`~django_typer.TyperCommand` class is very similar to using the BaseCommand_
class. The main difference is that we use Typer_'s decorators, classes and type annotations
to define the command's command line interface instead of argparse_ as BaseCommand_ expects.

Upstream Libraries
------------------

.. image:: /_static/img/django_typer_upstream.svg
   :align: right

django-typer_ merges the Django_ BaseCommand_ interface with the Typer_ interface and Typer_ itself
is built on top of click_. This means when using django-typer_ you will encounter interfaces and concepts
from *all three* of these upstream libraries:

* BaseCommand_

    Django_ has a good tutorial for understanding how commands are organized and built in Django_. If
    you are unfamiliar with using BaseCommand_ please first work through the 
    `polls Tutorial in the Django documentation <https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#module-django.core.management>`_.

* Typer_

    This tutorial can be completed without working through the `Typer tutorials <https://typer.tiangolo.com/tutorial/>`_,
    but familiarizing yourself with Typer_ will make this easier and will also be helpful when you
    want to define CLIs outside of Django_! We use the Typer_ interface to define
    `Arguments <https://typer.tiangolo.com/tutorial/arguments/>`_ and
    `Options <https://typer.tiangolo.com/tutorial/options/>`_ so please refer to the Typer_
    documentation for any questions about how to define these.

* click_

    Click_ interfaces and concepts are relatively hidden by Typer_, but occasionally you may need to
    refer to the click_ documentation when you want to implement more complex behaviors like passing
    `context parameters <https://click.palletsprojects.com/api/#context>`_. It is not necessary to
    familiarize yourself with click_ to use django-typer_, but you should know that it exists and is
    the engine behind much of this functionality.


Install django-typer_
---------------------

1. Install the latest release off PyPI_ :

    .. code:: bash

        pip install django-typer[rich]

    rich_ is a powerful library for rich text and beautiful formatting in the terminal.
    It is not required, but highly recommended for the best experience:

    .. note::

        If you install rich_, `traceback rendering <https://rich.readthedocs.io/en/stable/traceback.html>`_
        will be enabled by default. Refer to the :ref:`how-to <configure-rich-exception-tracebacks>` if
        you would like to disable it.


2. Add ``django_typer`` to your ``INSTALLED_APPS`` setting:

    .. code:: python

        INSTALLED_APPS = [
            ...
            'django_typer',
        ]

    .. note::

        Adding django_typer to INSTALLED_APPS is not strictly necessary if you do not wish to use shell
        tab completions or configure rich_ traceback rendering.


Convert the closepoll command to a :class:`~django_typer.TyperCommand`
----------------------------------------------------------------------

Recall our closepoll command from the `polls Tutorial in the Django documentation <https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#module-django.core.management>`_
looks like this:

.. code-block:: python

    from django.core.management.base import BaseCommand, CommandError
    from polls.models import Question as Poll


    class Command(BaseCommand):
        help = "Closes the specified poll for voting"

        def add_arguments(self, parser):
            parser.add_argument("poll_ids", nargs="+", type=int)

            # Named (optional) arguments
            parser.add_argument(
                "--delete",
                action="store_true",
                help="Delete poll instead of closing it",
            )

        def handle(self, *args, **options):
            for poll_id in options["poll_ids"]:
                try:
                    poll = Poll.objects.get(pk=poll_id)
                except Poll.DoesNotExist:
                    raise CommandError('Poll "%s" does not exist' % poll_id)

                poll.opened = False
                poll.save()

                self.stdout.write(
                    self.style.SUCCESS('Successfully closed poll "%s"' % poll_id)
                )

                if options["delete"]:
                    poll.delete()

Inherit from :class:`~django_typer.TyperCommand`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

To convert this to a :class:`~django_typer.TyperCommand` we need to inherit from :class:`~django_typer.TyperCommand`
instead and move the argument and option definitions from add_arguments into the method signature of handle. A minimal
conversion may look like this:

.. code-block:: python

    import typing as t

    from django_typer import TyperCommand
    from django.core.management.base import CommandError
    from polls.models import Question as Poll

    class Command(TyperCommand):
        help = "Closes the specified poll for voting"

        def handle(
            self,
            poll_ids: t.List[int],
            delete: bool = False,
        ):
            for poll_id in poll_ids:
                try:
                    poll = Poll.objects.get(pk=poll_id)
                except Poll.DoesNotExist:
                    raise CommandError('Poll "%s" does not exist' % poll_id)

                poll.opened = False
                poll.save()

                self.console.print(
                    f"Successfully closed poll {poll_id}",
                    style="bold green",
                )

                if delete:
                    poll.delete()

You'll note that we've removed add_arguments entirely and specified the arguments and options as parameters
to the handle method. django-typer_ will interpret the parameters on the handle() method as the command line
interface for the command. If we have rich_ installed the help for our new closepoll command will look like
this:


.. typer:: django_typer.examples.tutorial.step1.closepoll.Command:typer_app
    :prog: manage.py closepoll
    :width: 80
    :show-nested:
    :convert-png: latex
    :theme: dark

|

.. note::

    :class:`~django_typer.TyperCommand` adds the standard set of default options to the command line interface.


Add Helps with Type annotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

lambda


Add shell tab-completion suggestions for polls
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's very annoying to have to know the database primary key of the poll to close it. django-typer_ makes it
easy to add tab completion suggestions! Let's see wha that would look like:

