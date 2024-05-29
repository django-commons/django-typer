set -e  # Exit immediately if a command exits with a non-zero status.

if [ "$1" == "--no-fix" ]; then
    poetry run ruff format --check
    poetry run ruff format --line-length 80 --check examples
    poetry run ruff check --select I
    poetry run ruff check
else
    poetry run ruff format
    poetry run ruff format --line-length 80 examples
    poetry run ruff check --fix --select I
    poetry run ruff check --fix
fi

poetry run mypy django_typer
poetry run pyright
poetry check
poetry run pip check
cd ./doc
poetry run doc8 --ignore-path build --max-line-length 100 -q
cd ..
