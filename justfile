install:
    poetry install -E rich

check-types:
    poetry run mypy django_typer
    poetry run pyright

check-package:
    poetry check
    poetry run pip check

build-docs:
    cd ./doc && poetry run make html

docs:
    {{ just_executable() }} --justfile {{ justfile() }} build-docs
    python -c "from pathlib import Path; import webbrowser; webbrowser.open(Path('./doc/build/html/index.html').absolute().as_uri())"

check-docs-links:
    poetry run sphinx-build -b linkcheck -q -D linkcheck_timeout=5 ./doc/source ./doc/build > /dev/null 2>&1

check-docs:
    cd ./doc && poetry run doc8 --ignore-path build --max-line-length 100 -q

check-lint:
    poetry run ruff check --select I
    poetry run ruff check

check-format:
    poetry run ruff format --check
    poetry run ruff format --line-length 80 --check examples

check-readme:
    python -m readme_renderer ./README.md -o /tmp/README.html

format:
    just --fmt --unstable
    poetry run ruff format
    poetry run ruff format --line-length 80 examples

lint:
    poetry run ruff check --fix --select I
    poetry run ruff check --fix

fix-all:
    {{ just_executable() }} --justfile {{ justfile() }} format
    {{ just_executable() }} --justfile {{ justfile() }} lint

check-all:
    {{ just_executable() }} --justfile {{ justfile() }} check-lint
    {{ just_executable() }} --justfile {{ justfile() }} check-format
    {{ just_executable() }} --justfile {{ justfile() }} check-types
    {{ just_executable() }} --justfile {{ justfile() }} check-package
    {{ just_executable() }} --justfile {{ justfile() }} check-docs
    {{ just_executable() }} --justfile {{ justfile() }} check-docs-links
    {{ just_executable() }} --justfile {{ justfile() }} check-readme

test:
    poetry run pytest
