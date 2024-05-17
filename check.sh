poetry run ruff format django_typer
poetry run ruff format --line-length 80 django_typer/examples
poetry run ruff check --fix --select I django_typer
poetry run ruff check --fix django_typer
poetry run mypy django_typer
pyright
poetry check
poetry run pip check
