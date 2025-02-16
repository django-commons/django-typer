set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set unstable := true

default:
    @just --list

init:
    pip install pipx
    pipx ensurepath
    pipx install poetry
    poetry env use python
    poetry run pip install --upgrade pip setuptools wheel

install-precommit:
    poetry run pre-commit install

install *OPTS:
    poetry env use python
    poetry lock
    poetry install -E rich {{ OPTS }}
    poetry run pre-commit install

install-docs:
    poetry env use python
    poetry lock
    poetry install --with docs

install-translate:
    poetry env use python
    poetry lock
    poetry install --with translate

pin-dependency +PACKAGES:
    poetry run pip install -U {{ PACKAGES }}

check-types:
    poetry run mypy django_typer
    poetry run pyright

check-package:
    poetry check
    poetry run pip check

clean-docs:
    python -c "import shutil; shutil.rmtree('./doc/build', ignore_errors=True)"

clean-env:
    python -c "import shutil, sys; shutil.rmtree(sys.argv[1], ignore_errors=True)" $(poetry env info --path)

clean-git-ignored:
    git clean -fdX

# remove all non repository artifacts
clean: clean-docs clean-env clean-git-ignored

build-docs-html: install-docs
    poetry run sphinx-build --fresh-env --builder html --doctree-dir ./doc/build/doctrees ./doc/source ./doc/build/html

build-docs-pdf: install-docs
    poetry run sphinx-build --fresh-env --builder latexpdf --doctree-dir ./doc/build/doctrees ./doc/source ./doc/build/pdf

build-docs: build-docs-html

build-wheel:
    poetry build -f wheel

build-sdist:
    poetry build -f sdist

build: build-docs-html
    poetry build

open-docs:
    poetry run python -c "import webbrowser; webbrowser.open('file://$(pwd)/doc/build/html/index.html')"

docs: build-docs-html open-docs

docs-live:
    poetry run sphinx-autobuild doc/source doc/build --open-browser --watch django_typer --port 8000 --delay 1

check-docs-links:
    -poetry run sphinx-build -b linkcheck -Q -D linkcheck_timeout=10 ./doc/source ./doc/build
    poetry run python ./doc/broken_links.py

check-docs:
    poetry run doc8 --ignore-path ./doc/build --max-line-length 100 -q ./doc

check-lint:
    poetry run ruff check --select I
    poetry run ruff check

check-format:
    poetry run ruff format --check
    poetry run ruff format --line-length 80 --check examples

check-readme:
    poetry run python -m readme_renderer ./README.md -o /tmp/README.html

sort-imports:
    poetry run ruff check --fix --select I

format: sort-imports
    just --fmt --unstable
    poetry run ruff format
    poetry run ruff format --line-length 80 examples

lint: sort-imports
    poetry run ruff check --fix

fix: lint format

check: check-lint check-format check-types check-package check-docs check-docs-links check-readme

test-no-rich:
    poetry run pip uninstall -y rich
    poetry run pytest --cov-append -m no_rich

test-rich:
    poetry run pytest --cov-append -m rich

log-tests:
    poetry run python -m pytest --collect-only --disable-warnings -q --no-cov | poetry run python -c "from pathlib import Path; import sys; Path('./tests/tests.log').unlink(missing_ok=True); open('./tests/tests.log', 'a').close(); open('./tests/all_tests.log', 'w').writelines(sys.stdin)"

test-all: test-rich test-no-rich
    poetry run pip install colorama
    poetry run pytest --cov-append -m "not rich and not no_rich"
    poetry run pip uninstall -y colorama
    poetry run pytest --cov-append -k test_ctor_params

list-missed-tests: install log-tests test-all
    poetry run python ./tests/missed_tests.py

[script("bash")]
test-bash:
    poetry run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_bash tests/test_parser_completers.py tests/shellcompletion/test_bash.py

[script("zsh")]
test-zsh:
    poetry run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_zsh tests/test_parser_completers.py tests/shellcompletion/test_zsh.py

[script("powershell")]
test-powershell:
    poetry run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_powershell tests/test_parser_completers.py tests/test_parser_completers.py tests/shellcompletion/test_powershell.py::PowerShellTests tests/shellcompletion/test_powershell.py::PowerShellExeTests

[script("pwsh")]
test-pwsh:
    poetry run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_pwsh tests/test_parser_completers.py tests/shellcompletion/test_powershell.py::PWSHTests tests/shellcompletion/test_powershell.py::PWSHExeTests

[script("fish")]
test-fish:
    poetry run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_fish tests/test_parser_completers.py tests/shellcompletion/test_fish.py

test *TESTS:
    poetry run pytest --cov-append {{ TESTS }}

precommit:
    poetry run pre-commit

coverage:
    poetry run coverage combine --keep *.coverage
    poetry run coverage report
    poetry run coverage xml

run +ARGS:
    poetry run {{ ARGS }}

translate: install-translate
    poetry run ./manage.py translate --settings tests.settings.translate
