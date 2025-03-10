# Contributing

Contributions are encouraged! Please use the issue page to submit feature requests or bug reports. Issues with attached PRs will be given priority and have a much higher likelihood of acceptance. Please also open an issue and associate it with any submitted PRs.

We are actively seeking additional maintainers. If you're interested, please open an issue or [contact me](https://github.com/bckohan).

## Installation

### Install Just

We provide a platform independent justfile with recipes for all the development tasks. You should [install just](https://just.systems/man/en/installation.html) if it is not on your system already.

`django-typer` uses [uv](https://docs.astral.sh/uv) for environment, package, and dependency management. ``just setup`` will install the necessary build tooling if you do not already have it:

```shell
just setup
```

### Windows

There is a symbolic link to the top level examples directory in tests. On Windows to make sure this link is created you need to be in [developer mode](https://learn.microsoft.com/en-us/windows/apps/get-started/enable-your-device-for-development) and to configure git to allow symbolic links:

```console
git config --global core.symlinks true
```

## Documentation

`django-typer` documentation is generated using [Sphinx](https://www.sphinx-doc.org) with the [furo](https://github.com/pradyunsg/furo) theme. Any new feature PRs must provide updated documentation for the features added. To build the docs run doc8 to check for formatting issues then run Sphinx:

```bash
just docs  # builds docs
just check-docs  # lint the docs
just check-docs-links  # check for broken links in the docs
```

Run the docs with auto rebuild using:

```bash
just docs-live
```

## Static Analysis

`django-typer` uses [ruff](https://docs.astral.sh/ruff/) for Python linting, header import standardization and code formatting. [mypy](http://mypy-lang.org/) and [pyright](https://github.com/microsoft/pyright) are used for static type checking. Before any PR is accepted the following must be run, and static analysis tools should not produce any errors or warnings. Disabling certain errors or warnings where justified is acceptable:

To fix formatting and linting problems that are fixable run:

```bash
just fix
```

To run all static analysis without automated fixing you can run:

```bash
just check
```

## Running Tests

`django-typer` is set up to use [pytest](https://docs.pytest.org) to run unit tests. All the tests are housed in `tests`. Before a PR is accepted, all tests must be passing and the code coverage must be at 100%. A small number of exempted error handling branches are acceptable.

To run the full suite:

```shell
just test-all
```

To run a single test, or group of tests in a class:

```shell
just test <path_to_tests_file>::ClassName::FunctionName
```

For instance, to run all tests in BasicTests, and then just the test_call_command test you would do:

```shell
just test tests/test_basics.py::BasicTests
just test tests/test_basics.py::BasicTests::test_call_command
```

## Versioning

django-typer strictly adheres to [semantic versioning](https://semver.org).

## Issuing Releases

The release workflow is triggered by tag creation. You must have [git tag signing enabled](https://docs.github.com/en/authentication/managing-commit-signature-verification/signing-commits). Our justfile has a release shortcut:

```bash
    just release x.x.x
```

## Just Recipes

```
build                    # build src package and wheel
build-docs               # build the docs
build-docs-html          # build html documentation
build-docs-pdf           # build pdf documentation
check                    # run all static checks
check-docs               # lint the documentation
check-docs-links         # check the documentation links for broken links
check-format             # check if the code needs formatting
check-lint               # lint the code
check-package            # run package checks
check-readme             # check that the readme renders
check-types              # run static type checking
clean                    # remove all non repository artifacts
clean-docs               # remove doc build artifacts
clean-env                # remove the virtual environment
clean-git-ignored        # remove all git ignored files
coverage                 # generate the test coverage report
docs                     # build and open the documentation
docs-live                # serve the documentation, with auto-reload
fix                      # fix formatting, linting issues and import sorting
format                   # format the code and sort imports
install *OPTS            # update and install development dependencies
install-docs             # install documentation dependencies
install-precommit        # install git pre-commit hooks
install-psycopg3         # install with postgresql dependencies
install-translate        # install translation dependencies
install-uv               # install the uv package manager
lint                     # sort the imports and fix linting issues
list-missed-tests        # run the tests and report if any were not run - sanity check
log-tests                # run all tests and log them
manage *COMMAND          # run the django admin
open-docs                # open the html documentation
precommit                # run the pre-commit checks
release VERSION          # issue a relase for the given semver string (e.g. 2.1.0)
run +ARGS                # run the command in the virtual environment
setup python="python"    # setup the venv and pre-commit hooks
sort-imports             # sort the python imports
test *TESTS              # run tests
test-all                 # run all tests
test-bash                # test bash shell completions
test-fish                # test fish shell completions
test-lock +PACKAGES      # lock to specific python and versions of given dependencies
test-no-rich             # run the tests that require rich not to be installed
test-powershell          # test powershell shell completions
test-pwsh                # test pwsh shell completions
test-rich                # run the tests that require rich to be installed
test-zsh                 # test zsh shell completions
translate                # generate translations using google translate
validate_version VERSION # validate the given version string against the lib version
```