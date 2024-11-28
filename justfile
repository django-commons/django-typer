set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

install:
    poetry env use python
    poetry install -E rich

install-colorama:
    poetry run pip install colorama

install-docs:
    poetry env use python
    poetry install --with docs

check-types:
    poetry run mypy django_typer
    poetry run pyright

check-package:
    poetry check
    poetry run pip check

clean-docs:
    python -c "from shutil import rmtree; rmtree('./doc/build', ignore_errors=True)"

clean-env:
    python -c "import shutil, sys; shutil.rmtree(sys.argv[1])" $(poetry env info --path)

clean-git-ignored:
    git clean -fdX

clean: clean-docs clean-env clean-git-ignored

build-docs-html: install-docs
    poetry run sphinx-build --fresh-env --builder html --doctree-dir ./doc/build/doctrees ./doc/source ./doc/build/html

build-docs-pdf: install-docs
    poetry run sphinx-build --fresh-env --builder latexpdf --doctree-dir ./doc/build/doctrees ./doc/source ./doc/build/pdf

build-docs: build-docs-html

open-docs:
    python -c "from pathlib import Path; import webbrowser; webbrowser.open(Path('./doc/build/html/index.html').absolute().as_uri())"

docs: build-docs-html open-docs

check-docs-links:
    poetry run sphinx-build -b linkcheck -q -D linkcheck_timeout=5 ./doc/source ./doc/build > /dev/null 2>&1

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

format:
    just --fmt --unstable
    poetry run ruff format
    poetry run ruff format --line-length 80 examples

lint:
    poetry run ruff check --fix --select I
    poetry run ruff check --fix

fix-all: format lint

check-all: check-lint check-format check-types check-package check-docs check-docs-links check-readme

test-no-rich:
    poetry run pip uninstall -y rich
    poetry run pytest -m no_rich --cov-append

test-rich:
    poetry install -E rich
    poetry run pytest -m rich --cov-append

test: test-rich test-no-rich install-colorama
    poetry run pytest -m "not rich and not no_rich" --cov-append
    poetry run pip uninstall -y colorama
    poetry run pytest -k test_ctor_params --cov-append
