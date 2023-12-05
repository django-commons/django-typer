.. _Poetry: https://python-poetry.org/
.. _Pylint: https://www.pylint.org/
.. _isort: https://pycqa.github.io/isort/
.. _mypy: http://mypy-lang.org/
.. _django-pytest: https://pytest-django.readthedocs.io/en/latest/
.. _pytest: https://docs.pytest.org/en/stable/
.. _Sphinx: https://www.sphinx-doc.org/en/master/
.. _readthedocs: https://readthedocs.org/
.. _me: https://github.com/bckohan

Contributing
############

Contributions are encouraged! Please use the issue page to submit feature
requests or bug reports. Issues with attached PRs will be given priority and
have a much higher likelihood of acceptance. Please also open an issue and
associate it with any submitted PRs. That said, the aim is to keep this library
as lightweight as possible. Only features with broad based use cases will be
considered.

We are actively seeking additional maintainers. If you're interested, please
contact me_.


Installation
------------

`django-typer` uses Poetry_ for environment, package and dependency
management:

.. code-block::

    poetry install

Documentation
-------------

`django-typer` documentation is generated using Sphinx_ with the
readthedocs_ theme. Any new feature PRs must provide updated documentation for
the features added. To build the docs run:

.. code-block::

    cd ./doc
    poetry run make html


Static Analysis
---------------

`django-typer` uses Pylint_ for python linting and mypy_ for static type
checking. Header imports are also standardized using isort_. Before any PR is
accepted the following must be run, and static analysis tools should not
produce any errors or warnings. Disabling certain errors or warnings where
justified is acceptable:

.. code-block::

    poetry run isort django_typer
    poetry run pylint django_typer
    poetry run mypy django_typer
    poetry run doc8 -q doc
    poetry check
    poetry run pip check
    poetry run safety check --full-report
    poetry run python -m readme_renderer ./README.rst


Running Tests
-------------

`django-typer` is setup to use pytest_ to run unit tests. All the tests are
housed in django_typer/tests/tests.py. Before a PR is accepted, all tests
must be passing and the code coverage must be at 100%. A small number of
exempted error handling branches are acceptable.

To run the full suite:

.. code-block::

    poetry run pytest

To run a single test, or group of tests in a class:

.. code-block::

    poetry run pytest <path_to_tests_file>::ClassName::FunctionName

For instance to run all tests in BasicTests, and then just the
test_call_command test you would do:

.. code-block::

    poetry run pytest django_typer/tests/tests.py::BasicTests
    poetry run pytest django_typer/tests/tests.py::BasicTests::test_call_command
