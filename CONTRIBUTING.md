# Contributing

Contributions are encouraged! Please use the issue page to submit feature requests or bug reports. Issues with attached PRs will be given priority and have a much higher likelihood of acceptance. Please also open an issue and associate it with any submitted PRs.

We are actively seeking additional maintainers. If you're interested, please open an issue or [contact me](https://github.com/bckohan).

## Installation

`django-typer` uses [Poetry](https://python-poetry.org/) for environment, package, and dependency management:

```shell
poetry install
```

### Windows

There is a symbolic link to the top level examples directory in tests. On Windows to make sure this link is created you need to be in developer mode and to configure git to allow symbolic links:

```console
git config core.symlinks true
```

## Documentation

`django-typer` documentation is generated using [Sphinx](https://www.sphinx-doc.org) with the [furo](https://github.com/pradyunsg/furo) theme. Any new feature PRs must provide updated documentation for the features added. To build the docs run doc8 to check for formatting issues then run Sphinx:

```bash
cd ./doc
poetry run doc8 --ignore-path build --max-line-length 100
poetry run make html
```

## Static Analysis

`django-typer` uses [ruff](https://docs.astral.sh/ruff/) for Python linting, header import standardization and code formatting. [mypy](http://mypy-lang.org/) and [pyright](https://github.com/microsoft/pyright) are used for static type checking. Before any PR is accepted the following must be run, and static analysis tools should not produce any errors or warnings. Disabling certain errors or warnings where justified is acceptable:

```bash
./check.sh
```

To run static analysis without automated fixing you can run:

```bash
./check.sh --no-fix
```

## Running Tests

`django-typer` is set up to use [pytest](https://docs.pytest.org) to run unit tests. All the tests are housed in `tests`. Before a PR is accepted, all tests must be passing and the code coverage must be at 100%. A small number of exempted error handling branches are acceptable.

To run the full suite:

```shell
poetry run pytest
```

To run a single test, or group of tests in a class:

```shell
poetry run pytest <path_to_tests_file>::ClassName::FunctionName
```

For instance, to run all tests in BasicTests, and then just the test_call_command test you would do:

```shell
poetry run pytest tests/test_basics.py::BasicTests
poetry run pytest tests/test_basics.py::BasicTests::test_call_command
```

## Versioning

django-typer strictly adheres to [semantic versioning](https://semver.org).
