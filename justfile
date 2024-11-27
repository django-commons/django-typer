set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]

install:
    poetry env use python
    poetry install -E rich

check-types:
    poetry run mypy django_typer
    poetry run pyright

check-package:
    poetry check
    poetry run pip check

clean-docs:
    python -c "from shutil import rmtree; rmtree('./doc/build', ignore_errors=True)"

build-docs-html:
    poetry run sphinx-build --fresh-env --builder html --doctree-dir ./doc/build/doctrees ./doc/source ./doc/build/html

build-docs: build-docs-html

build-docs-pdf:
    poetry run sphinx-build --fresh-env --builder latexpdf --doctree-dir ./doc/build/doctrees ./doc/source ./doc/build/pdf

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

test:
    poetry run pytest --cov-append
