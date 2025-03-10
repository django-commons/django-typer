set windows-shell := ["powershell.exe", "-NoLogo", "-Command"]
set unstable := true
set script-interpreter := ['uv', 'run', '--script']

export PYTHONPATH := source_directory()

[private]
default:
    @just --list --list-submodules

# run the django admin
[script]
manage *COMMAND:
    import os
    import sys
    import shlex
    from pathlib import Path
    from django.core import management
    os.environ.setdefault("DJANGO_SETTINGS_MODULE", "tests.settings.base")
    management.execute_from_command_line(sys.argv + shlex.split('{{ COMMAND }}'))

# install the uv package manager
[linux]
[macos]
install-uv:
    curl -LsSf https://astral.sh/uv/install.sh | sh

# install the uv package manager
[windows]
install-uv:
    powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"

# setup the venv and pre-commit hooks
setup python="python":
    uv venv -p {{ python }}
    @just run pre-commit install

# install git pre-commit hooks
install-precommit:
    @just run pre-commit install

# update and install development dependencies
install *OPTS:
    uv sync {{ OPTS }}
    @just run pre-commit install

# install documentation dependencies
install-docs:
    uv sync --group docs --all-extras

install-psycopg3:
    uv sync --group psycopg3

# install translation dependencies
install-translate:
    uv sync --group translate

[script]
_lock-python:
    import tomlkit
    import sys
    f='pyproject.toml'
    d=tomlkit.parse(open(f).read())
    d['project']['requires-python']='=={}'.format(sys.version.split()[0])
    open(f,'w').write(tomlkit.dumps(d))

# lock to specific python and versions of given dependencies
test-lock +PACKAGES: _lock-python
    uv add {{ PACKAGES }}

# run static type checking
check-types:
    @just run mypy
    @just run pyright

# run package checks
check-package:
    @just run pip check

# remove doc build artifacts
[script]
clean-docs:
    import shutil
    shutil.rmtree('./doc/build', ignore_errors=True)

# remove the virtual environment
[script]
clean-env:
    import shutil
    import sys
    shutil.rmtree(".venv", ignore_errors=True)

# remove all git ignored files
clean-git-ignored:
    git clean -fdX

# remove all non repository artifacts
clean: clean-docs clean-git-ignored clean-env

# build html documentation
build-docs-html: install-docs
    @just run sphinx-build --fresh-env --builder html --doctree-dir ./doc/build/doctrees ./doc/source ./doc/build/html

# build pdf documentation
build-docs-pdf: install-docs
    @just run sphinx-build --fresh-env --builder latexpdf --doctree-dir ./doc/build/doctrees ./doc/source ./doc/build/pdf

# build the docs
build-docs: build-docs-html

build:
    uv build

# open the html documentation
[script]
open-docs:
    import os
    import webbrowser
    webbrowser.open(f'file://{os.getcwd()}/doc/build/html/index.html')

# build and open the documentation
docs: build-docs-html open-docs

# serve the documentation, with auto-reload
docs-live: install-docs
    @just run sphinx-autobuild doc/source doc/build --open-browser --watch src --port 8000 --delay 1

_link_check:
    -uv run sphinx-build -b linkcheck -Q -D linkcheck_timeout=10 ./doc/source ./doc/build

# check the documentation links for broken links
[script]
check-docs-links: _link_check
    import os
    import sys
    import json
    from pathlib import Path
    # The json output isn't valid, so we have to fix it before we can process.
    data = json.loads(f"[{','.join((Path(os.getcwd()) / 'doc/build/output.json').read_text().splitlines())}]")
    broken_links = [link for link in data if link["status"] not in {"working", "redirected", "unchecked", "ignored"}]
    if broken_links:
        for link in broken_links:
            print(f"[{link['status']}] {link['filename']}:{link['lineno']} -> {link['uri']}", file=sys.stderr)
        sys.exit(1)

# lint the documentation
check-docs:
    @just run doc8 --ignore-path ./doc/build --max-line-length 100 -q ./doc

# lint the code
check-lint:
    @just run ruff check --select I
    @just run ruff check

# check if the code needs formatting
check-format:
    @just run ruff format --check
    @just run ruff format --line-length 80 --check examples

# check that the readme renders
check-readme:
    @just run python -m readme_renderer ./README.md -o /tmp/README.html

# sort the python imports
sort-imports:
    @just run ruff check --fix --select I

# format the code and sort imports
format: sort-imports
    just --fmt --unstable
    @just run ruff format
    @just run ruff format --line-length 80 examples

# sort the imports and fix linting issues
lint: sort-imports
    @just run ruff check --fix

# fix formatting, linting issues and import sorting
fix: lint format

# run all static checks
check: check-lint check-format check-types check-package check-docs check-docs-links check-readme

# run the tests that require rich not to be installed
test-no-rich:
    uv pip uninstall rich
    uv run pytest --cov-append -m no_rich

# run the tests that require rich to be installed
test-rich:
    uv run pytest --cov-append -m rich

# run all tests
test-all: test-rich test-no-rich
    uv pip install colorama
    uv run pytest --cov-append -m "not rich and not no_rich"
    uv pip uninstall colorama
    uv run pytest --cov-append -k test_ctor_params

_log-tests:
    uv run pytest --collect-only --disable-warnings -q --no-cov

# run all tests and log them
[script]
log-tests:
    from pathlib import Path
    import sys
    Path('./tests/tests.log').unlink(missing_ok=True)
    open('./tests/tests.log', 'a').close()
    open('./tests/all_tests.log', 'w').writelines(sys.stdin)

# run the tests and report if any were not run - sanity check
[script]
list-missed-tests: install log-tests test-all
    import sys
    from pathlib import Path
    test_log = Path(__file__).parent / "tests.log"
    all_tests = Path(__file__).parent / "all_tests.log"
    assert test_log.is_file() and all_tests.is_file()

    tests_run = set(test_log.read_text().splitlines())
    all_tests = set(all_tests.read_text().splitlines()[0:-2])
    if tests_run != all_tests:
        print("Not all tests were run:", file=sys.stderr)
        for test in all_tests - tests_run:
            print(test, file=sys.stderr)
        sys.exit(1)

# test bash shell completions
[script("bash")]
test-bash:
    uv run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_bash tests/test_parser_completers.py tests/shellcompletion/test_bash.py

# test zsh shell completions
[script("zsh")]
test-zsh:
    uv run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_zsh tests/test_parser_completers.py tests/shellcompletion/test_zsh.py

# test powershell shell completions
[script("powershell")]
test-powershell:
    uv run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_powershell tests/test_parser_completers.py tests/test_parser_completers.py tests/shellcompletion/test_powershell.py::PowerShellTests tests/shellcompletion/test_powershell.py::PowerShellExeTests

# test pwsh shell completions
[script("pwsh")]
test-pwsh:
    uv run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_pwsh tests/test_parser_completers.py tests/shellcompletion/test_powershell.py::PWSHTests tests/shellcompletion/test_powershell.py::PWSHExeTests

# test fish shell completions
[script("fish")]
test-fish:
    uv run pytest --cov-append tests/shellcompletion/test_shell_resolution.py::TestShellResolution::test_fish tests/test_parser_completers.py tests/shellcompletion/test_fish.py

# run tests
test *TESTS:
    @just run pytest --cov-append {{ TESTS }}

# run the pre-commit checks
precommit:
    @just run pre-commit

# generate the test coverage report
coverage:
    @just run coverage combine --keep *.coverage
    @just run coverage report
    @just run coverage xml

# run the command in the virtual environment
run +ARGS:
    uv run {{ ARGS }}

# generate translations using google translate
translate: install-translate
    @just manage translate --settings tests.settings.translate

# validate the given version string against the lib version
[script]
validate_version VERSION:
    import re
    import tomllib
    import django_typer
    from packaging.version import Version
    raw_version = "{{ VERSION }}".lstrip("v")
    version_obj = Version(raw_version)
    # the version should be normalized
    assert str(version_obj) == raw_version
    # make sure all places the version appears agree
    assert raw_version == tomllib.load(open('pyproject.toml', 'rb'))['project']['version']
    assert raw_version == django_typer.__version__
    print(raw_version)

# issue a relase for the given semver string (e.g. 2.1.0)
release VERSION:
    @just validate_version v{{ VERSION }}
    git tag -s v{{ VERSION }} -m "{{ VERSION }} Release"
    git push origin v{{ VERSION }}
