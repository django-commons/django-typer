.. include:: ./refs.rst

========
Tutorial
========

Using the :class:`~django_typer.TyperCommand` class is very similar to using the BaseCommand_
class. The main difference is that we use Typer_'s decorators, classes and type annotations
to define the command's command line interface instead of argparse_ as BaseCommand_ expects.

Upstream Libraries
------------------

.. only:: html

    .. image:: /_static/img/django_typer_upstream.svg
        :align: right

.. only:: latex

    .. image:: /_static/img/django_typer_upstream.pdf
        :align: right

django-typer_ merges the Django_ BaseCommand_ interface with the Typer_ interface and Typer_ itself
is built on top of click_. This means when using django-typer_ you will encounter interfaces and
concepts from *all three* of these upstream libraries:

* BaseCommand_

    Django_ has a good tutorial for understanding how commands are organized and built in Django_. If
    you are unfamiliar with using BaseCommand_ please first work through the
    `polls Tutorial in the Django documentation <https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#module-django.core.management>`_.

* Typer_

    This tutorial can be completed without working through the `Typer tutorials <https://typer.tiangolo.com/tutorial/>`_,
    but familiarizing yourself with Typer_ will make this easier and will also be helpful when you
    want to define CLIs outside of Django_! We use the Typer_ interface to define Arguments_ and
    Options_ so please refer to the Typer_ documentation for any questions about how to define
    these.

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

        pip install "django-typer[rich]"

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
        tab completions or configure `rich traceback rendering <https://rich.readthedocs.io/en/stable/traceback.html>`_.


Convert the closepoll command to a :class:`~django_typer.TyperCommand`
----------------------------------------------------------------------

Recall our closepoll command from the `polls Tutorial in the Django documentation <https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#module-django.core.management>`_
looks like this:

.. code-block:: python
    :linenos:

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
                    raise CommandError(f'Poll "{poll_id}" does not exist')

                poll.opened = False
                poll.save()

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully closed poll "{poll.id}"')
                )

                if options["delete"]:
                    poll.delete()

Inherit from :class:`~django_typer.TyperCommand`
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We first need to change the inheritance to :class:`~django_typer.TyperCommand` and then move the
argument and option definitions from add_arguments into the method signature of handle. A minimal
conversion may look like this:

.. code-block:: python
    :linenos:

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
                    raise CommandError(f'Poll "{poll_id}" does not exist')

                poll.opened = False
                poll.save()

                self.stdout.write(
                    self.style.SUCCESS(f'Successfully closed poll "{poll.id}"')
                )

                if delete:
                    poll.delete()

You'll note that we've removed add_arguments entirely and specified the arguments and options as
parameters to the handle method. django-typer_ will interpret the parameters on the handle() method
as the command line interface for the command. If we have rich_ installed the help for our new
closepoll command will look like this:


.. typer:: django_typer.examples.tutorial.step1.closepoll.Command:typer_app
    :prog: manage.py closepoll
    :width: 80
    :show-nested:
    :convert-png: latex
    :theme: dark

|

.. note::

    :class:`~django_typer.TyperCommand` adds the standard set of default options to the command
    line interface, with the exception of verbosity, which can be


Add Helps with Type annotations
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Typer_ allows us to use `Annotated types <https://docs.python.org/3/library/typing.html#typing.Annotated>`_
to add additional controls to how the command line interface behaves. The most common use case for
this is to add help text to the command line interface. We will annotate our parameter type hints
with one of two Typer_ parameter types, either Argument or Option. Arguments_ are positional
parameters and Options_ are named parameters (i.e. `--delete`). In our polls example, the poll_ids
are arguments and the delete flag is an option. Here is what that would look like:

.. code-block:: python
    :linenos:

    import typing as t

    from django.core.management.base import CommandError
    from django.utils.translation import gettext_lazy as _
    from typer import Argument, Option

    from django_typer import TyperCommand
    from polls.models import Question as Poll


    class Command(TyperCommand):
        help = "Closes the specified poll for voting"

        def handle(
            self,
            poll_ids: t.Annotated[
                t.List[int], Argument(help=_("The database IDs of the poll(s) to close."))
            ],
            delete: t.Annotated[
                bool, Option(help=_("Delete poll instead of closing it."))
            ] = False,
        ):
            # ...

See that our help text now shows up in the command line interface. Also note, that lazy translations
work for the help strings. Typer_ also allows us to specify our help text in the docstrings of the
command function or class, in this case either Command or handle() - but docstrings are not
available to the translation system. If translation is not necessary and your help text is extensive
or contains markup the docstring may be the more appropriate place to put it.

.. typer:: django_typer.examples.tutorial.step2.closepoll.Command:typer_app
    :prog: manage.py closepoll
    :width: 80
    :show-nested:
    :convert-png: latex
    :theme: dark

|

.. note::

    On Python <=3.8 you will need to import Annotated from typing_extensions_ instead of the standard
    library.


Defining custom and reusable parameter types
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

We may have other commands that need to operate on Poll objects from given poll ids. We could
duplicate our for loop that loads Poll objects from ids, but that wouldn't be very DRY. Instead,
Typer_ allows us to define custom parsers for arbitrary parameter types. Lets see what that would
look like if we used the Poll class as our type hint:

.. code-block:: python
    :linenos:

    import typing as t

    # ...

    def get_poll_from_id(poll: t.Union[str, Poll]) -> Poll:
        # our parser may be passed a Poll object depending on how
        # users might call our command from code - so we must check
        # to be sure we have something to parse at all!
        if isinstance(poll, Poll):
            return poll
        try:
            return Poll.objects.get(pk=int(poll))
        except Poll.DoesNotExist:
            raise CommandError(f'Poll "{poll_id}" does not exist')


    class Command(TyperCommand):

        def handle(
            self,
            polls: t.Annotated[
                t.List[Poll],  # change our type hint to a list of Polls!
                Argument(
                    parser=get_poll_from_id,  # pass our parser to the Argument!
                    help=_("The database IDs of the poll(s) to close."),
                ),
            ],
            delete: t.Annotated[
                bool,
                Option(
                    "--delete",  # we can also get rid of that unnecessary --no-delete flag
                    help=_("Delete poll instead of closing it."),
                ),
            ] = False,
        ):
            """
            Closes the specified poll for voting.

            As mentioned in the last section, helps can also
            be set in the docstring
            """
            for poll in polls:
                poll.opened = False
                poll.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully closed poll "{poll.id}"')
                )
                if delete:
                    poll.delete()



.. typer:: django_typer.examples.tutorial.step3.closepoll.Command:typer_app
    :prog: manage.py closepoll
    :width: 80
    :show-nested:
    :convert-png: latex
    :theme: dark

|

django-typer_ offers some built-in :mod:`~django_typer.parsers` that can be used for
common Django_ types. For example, the :class:`~django_typer.parsers.ModelObjectParser` can
be used to fetch a model object from a given field. By default it will use the primary key,
so we could rewrite the relevant lines above like so:

.. code-block:: python

    from django_typer.parsers import ModelObjectParser

    # ...

    t.Annotated[
        t.List[Poll],
        Argument(
            parser=ModelObjectParser(Poll),
            help=_("The database IDs of the poll(s) to close.")
        )
    ]

    # ...

Add shell tab-completion suggestions for polls
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

It's very annoying to have to know the database primary key of the poll to close it. django-typer_ makes it
easy to add tab completion suggestions! You can always
`implement your own completer functions <https://click.palletsprojects.com/en/8.1.x/shell-completion/#custom-type-completion>`_,
but as with, :mod:`~django_typer.parsers`, there are some out-of-the-box :mod:`~django_typer.completers` that
make this easy. Let's see what the relevant updates to our closepoll command would look like:

.. code-block:: python

    from django_typer.parsers import ModelObjectParser
    from django_typer.completers import ModelObjectCompleter

    # ...

    t.Annotated[
        t.List[Poll],
        Argument(
            parser=ModelObjectParser(Poll),
            shell_complete=ModelObjectCompleter(Poll, help_field='question_text'),
            help=_("The database IDs of the poll(s) to close.")
        )
    ]

    # ...

.. note::

    For tab-completions to work you will need to
    :ref:`install the shell completion scripts for your shell <shellcompletions>`.


Putting it all together
~~~~~~~~~~~~~~~~~~~~~~~

When we're using a :class:`~django_typer.parsers.ModelObjectParser` and
:class:`~django_typer.completers.ModelObjectCompleter` we can use the
:func:`~django_typer.model_parser_completer` convenience function to reduce the amount
of boiler plate. Let's put everything together and see what our full-featured refactored
closepoll command looks like:

.. code-block:: python
    :linenos:

    import typing as t

    from django.utils.translation import gettext_lazy as _
    from typer import Argument, Option

    from django_typer import TyperCommand, model_parser_completer
    from polls.models import Question as Poll


    class Command(TyperCommand):
        help = _("Closes the specified poll for voting.")

        def handle(
            self,
            polls: Annotated[
                t.List[Poll],
                Argument(
                    **model_parser_completer(Poll, help_field="question_text"),
                    help=_("The database IDs of the poll(s) to close."),
                ),
            ],
            delete: Annotated[
                bool, Option(help=_("Delete poll instead of closing it.")),
            ] = False,
        ):
            for poll in polls:
                poll.opened = False
                poll.save()
                self.stdout.write(
                    self.style.SUCCESS(f'Successfully closed poll "{poll.id}"')
                )
                if delete:
                    poll.delete()


.. only:: html

    .. image:: /_static/img/closepoll_example.gif
        :align: center

.. only:: latex

    .. image:: /_static/img/closepoll_example.png
        :align: center