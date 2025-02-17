set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set unstable := true

# list all available commands
default:
    @just --list

# install build tooling
init python="python":
    pip install pipx
    pipx ensurepath
    pipx install poetry
    poetry env use {{ python }}
    poetry run pip install --upgrade pip setuptools wheel

# install git pre-commit hooks
install-precommit:
    poetry run pre-commit install

# update and install development dependencies
install *OPTS:
    poetry lock
    poetry install -E rich {{ OPTS }}
    poetry run pre-commit install

# install documentation dependencies
install-docs:
    poetry lock
    poetry install --with docs

# install translation dependencies
install-translate:
    poetry lock
    poetry install --with translate

# install a dependency to a specific version e.g. just pin-dependency Django~=5.1.0
pin-dependency +PACKAGES:
    poetry run pip install -U {{ PACKAGES }}

# run static type checking
check-types:
    poetry run mypy django_typer
    poetry run pyright

# run package checks
check-package:
    poetry check
    poetry run pip check

# remove doc build artifacts
clean-docs:
    python -c "import shutil; shutil.rmtree('./doc/build', ignore_errors=True)"

# remove the virtual environment
clean-env:
    python -c "import shutil, sys; shutil.rmtree(sys.argv[1], ignore_errors=True)" $(poetry env info --path)

# remove all git ignored files
clean-git-ignored:
    git clean -fdX

# remove all non repository artifacts
clean: clean-docs clean-env clean-git-ignored

# build html documentation
build-docs-html: install-docs
    poetry run sphinx-build --fresh-env --builder html --doctree-dir ./doc/build/doctrees ./doc/source ./doc/build/html

# build pdf documentation
build-docs-pdf: install-docs
    poetry run sphinx-build --fresh-env --builder latexpdf --doctree-dir ./doc/build/doctrees ./doc/source ./doc/build/pdf

# build the docs
build-docs: build-docs-html

# build the wheel distribution
build-wheel:
    poetry build -f wheel

# build the source distribution
build-sdist:
    poetry build -f sdist

# build docs and package
build: build-docs-html
    poetry build

# open the html documentation
open-docs:
    poetry run python -c "import webbrowser; webbrowser.open('file://$(pwd)/doc/build/html/index.html')"

# build and open the documentation
docs: build-docs-html open-docs

# serve the documentation, with auto-reload
docs-live:
    poetry run sphinx-autobuild doc/source doc/build --open-browser --watch django_typer --port 8000 --delay 1

# check the documentation links for broken links
check-docs-links:
    -poetry run sphinx-build -b linkcheck -Q -D linkcheck_timeout=10 ./doc/source ./doc/build
    poetry run python ./doc/broken_links.py

# lint the documentation
check-docs:
    poetry run doc8 --ignore-path ./doc/build --max-line-length 100 -q ./doc

# lint the code
check-lint:
    poetry run ruff check --select I
    poetry run ruff check

# check if the code needs formatting
check-format:
    poetry run ruff format --check
    poetry run ruff format --line-length 80 --check examples

# check that the readme renders
check-readme:
    poetry run python -m readme_renderer ./README.md -o /tmp/README.html

# sort the python imports
sort-imports:
    poetry run ruff check --fix --select I

# format the code and sort imports
format: sort-imports
    just --fmt --unstable
    poetry run ruff format
    poetry run ruff format --line-length 80 examples

# sort the imports and fix linting issues
lint: sort-imports
    poetry run ruff check --fix

# fix formatting, linting issues and import sorting
fix: lint format

# run all static checks
check: check-lint check-format check-types check-package check-docs check-docs-links check-readme

# run the tests that require rich not to be installed
test-no-rich:
    poetry run pip uninstall -y rich
    poetry run pytest --cov-append -m no_rich

# run the tests that require rich to be installed
test-rich:
    poetry run pytest --cov-append -m rich

# run all tests and log them
log-tests:
    poetry run python -m pytest --collect-only --disable-warnings -q --no-cov | poetry run python -c "from pathlib import Path; import sys; Path('./tests/tests.log').unlink(missing_ok=True); open('./tests/tests.log', 'a').close(); open('./tests/all_tests.log', 'w').writelines(sys.stdin)"

# run all tests
test-all: test-rich test-no-rich
    poetry run pip install colorama
    poetry run pytest --cov-append -m "not rich and not no_rich"
    poetry run pip uninstall -y colorama
    poetry run pytest --cov-append -k test_ctor_params

# run the tests and report if any were not run - sanity check
list-missed-tests: install log-tests test-all
    poetry run python ./tests/missed_tests.py

# test bash shell completions
[script("bash")]
test-bash:
    poetry run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_bash tests/test_parser_completers.py tests/shellcompletion/test_bash.py

# test zsh shell completions
[script("zsh")]
test-zsh:
    poetry run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_zsh tests/test_parser_completers.py tests/shellcompletion/test_zsh.py

# test powershell shell completions
[script("powershell")]
test-powershell:
    poetry run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_powershell tests/test_parser_completers.py tests/test_parser_completers.py tests/shellcompletion/test_powershell.py::PowerShellTests tests/shellcompletion/test_powershell.py::PowerShellExeTests

# test pwsh shell completions
[script("pwsh")]
test-pwsh:
    poetry run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_pwsh tests/test_parser_completers.py tests/shellcompletion/test_powershell.py::PWSHTests tests/shellcompletion/test_powershell.py::PWSHExeTests

# test fish shell completions
[script("fish")]
test-fish:
    poetry run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_fish tests/test_parser_completers.py tests/shellcompletion/test_fish.py

# run tests
test *TESTS:
    poetry run pytest --cov-append {{ TESTS }}

# run the pre-commit checks
precommit:
    poetry run pre-commit

# generate the test coverage report
coverage:
    poetry run coverage combine --keep *.coverage
    poetry run coverage report
    poetry run coverage xml

# run the command in the virtual environment
run +ARGS:
    poetry run {{ ARGS }}

# generate translations using google translate
translate: install-translate
    poetry run ./manage.py translate --settings tests.settings.translate
