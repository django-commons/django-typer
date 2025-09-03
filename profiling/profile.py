#!python

import bisect
import json
import os
import platform
import shutil
import subprocess
import sys
import typing as t
from dataclasses import asdict, dataclass, is_dataclass
from hashlib import sha256
from pathlib import Path
from pprint import pprint

import django
import typer

from django_typer import VERSION as django_typer_version

app = typer.Typer()


def dataclass_encoder(obj):
    if is_dataclass(obj):
        return asdict(obj)
    raise TypeError(f"Type {type(obj)} not serializable")


@dataclass(frozen=True)
class EnvKey:
    django_typer: t.Tuple[int, int, int]
    python: t.Tuple[int, int]
    django: t.Tuple[int, int]
    typer: t.Tuple[int, int]

    def astuple(self):
        return (self.django_typer, self.python, self.django, self.typer)


@dataclass(frozen=True)
class Platform:
    os: str
    arch: str
    name: str


@dataclass(frozen=True)
class RunKey:
    cmd: str
    """
    The command that was run.
    """

    typer: bool
    """
    Is this a Typer command?
    """

    app: bool
    """
    Is the django_typer app installed?
    """

    rich: bool
    """
    Is rich installed?
    """

    help: bool
    """
    Is this a help run?
    """

    def __hash__(self):
        """
        Python randomizes hashes across interpreter runs so we need to define our own
        repeatable hash
        """
        return int.from_bytes(
            sha256(
                f"{self.cmd}|{int(self.typer)}|{int(self.app)}|"
                f"{int(self.rich)}|{int(self.help)}".encode("utf-8")
            ).digest(),
            byteorder="big",
        )


django_admin = os.path.join(os.environ["VIRTUAL_ENV"], "bin", "django-admin")

no_typer = {"DJANGO_SETTINGS_MODULE": "profiling.settings.no_typer"}
with_typer = {"DJANGO_SETTINGS_MODULE": "profiling.settings.with_typer"}
with_typer_app = {"DJANGO_SETTINGS_MODULE": "profiling.settings.with_typer_app"}
polls = {"DJANGO_SETTINGS_MODULE": "profiling.settings.polls"}
polls_no_typer = {"DJANGO_SETTINGS_MODULE": "profiling.settings.polls_no_typer"}
polls_with_typer = {"DJANGO_SETTINGS_MODULE": "profiling.settings.polls_with_typer"}

pythonpath = os.path.realpath(__file__ + "/../..")

run_counts = 50

rich_installed = False
try:
    import rich  # noqa: F401

    rich_installed = True
except ImportError:
    pass

profiling_dir = os.path.realpath(__file__ + "/..")
profile_file = os.path.realpath(__file__ + "/../profile.json")


def get_platform() -> Platform:
    if shutil.which("scutil"):
        computer = (
            subprocess.check_output(["scutil", "--get", "ComputerName"])
            .strip()
            .decode()
        )
    else:
        computer = platform.node()
    return Platform(
        os=platform.system().lower(), arch=platform.machine().lower(), name=computer
    )


def run_command(*cmd, **env):
    result = subprocess.run(
        [*cmd],
        capture_output=True,
        text=True,
        env={"PYTHONPATH": pythonpath, "VIRTUAL_ENV": os.environ["VIRTUAL_ENV"], **env},
    )
    stdout = result.stdout
    if stdout:
        import json

        try:
            stdout = json.loads(result.stdout)
        except json.JSONDecodeError:
            pass
    return stdout, result.stderr, result.returncode


def time_command(*cmd, **env):
    stdout, stderr, retcode = run_command("time", *cmd, **env)
    real_seconds = float(stderr.split("real")[0]) if stderr else None
    return stdout, stderr, retcode, real_seconds


def import_trace(*cmd, save=None, **env):
    _, stderr, _ = run_command(sys.executable, "-X", "importtime", *cmd, **env)
    imports = {}
    for line in stderr.splitlines()[1:]:
        line = line.strip()
        if line and line.startswith("import time:"):
            slf, cum, pkg = line[len("import time: ") :].strip().split("|")
            slf = int(slf.strip())
            cum = int(cum.strip())
            pkg = pkg.strip()
            imports[pkg] = (slf, cum)
    if save:
        with open(profiling_dir + "/" + save.replace("_.", "."), "wt") as f:
            f.write(stderr)
    return imports


def load():
    if os.path.exists(profile_file):
        with open(profile_file, "r") as f:
            profile_data = json.load(f)
            for key, value in profile_data.items():
                value["env"] = EnvKey(**{k: tuple(v) for k, v in value["env"].items()})
                value["platform"] = Platform(**value["platform"])
                profile_data[key] = value
                for id, run in value["runs"].items():
                    run["run"] = RunKey(**run["run"])
                    assert id == str(hash(run["run"]))
            return profile_data
    return {}


@app.command(help="Load fixture data.")
def load_fixtures():
    stdout, stderr, retcode = run_command(django_admin, "migrate", **polls)
    if retcode == 0:
        print(stdout)
    else:
        print(stderr)
    stdout, stderr, retcode = run_command(
        django_admin, "loaddata", str(Path(__file__).parent / "polls.json"), **polls
    )
    if retcode == 0:
        print(stdout)
    else:
        print(stderr)


@app.command(
    help="Generate profiling data for django_typer in the current environment."
)
def generate():
    load_fixtures()
    profile_data = load()

    env_key = EnvKey(
        django_typer=django_typer_version,
        python=sys.version_info[0:2],
        django=django.VERSION[:2],
        typer=tuple(int(v) for v in typer.__version__.split(".")[:2]),
    )

    # json files dont allow tuples to be keys so to keep the latest data at the end of
    # the list we have to do a little manual sorting
    env_keys = sorted([run["env"].astuple() for run in profile_data.values()])
    pos = bisect.bisect_left(env_keys, env_key.astuple()) or 0
    pos_str = str(pos)
    if pos_str in profile_data:
        if profile_data[pos_str]["env"] != env_key:
            for idx in reversed(
                range(pos, max((int(i) for i in profile_data.keys())) + 1)
            ):
                if str(idx) in profile_data:
                    profile_data[str(idx + 1)] = profile_data.pop(str(idx))

    profile_data.setdefault(pos_str, {"env": env_key, "runs": {}})
    profile_data[pos_str]["platform"] = get_platform()

    last_idx = pos - 1
    while last_idx >= 0 and str(last_idx) not in profile_data:
        last_idx -= 1

    for hlp in [False, True]:
        for cmd, env in [
            (("minimal", "5"), no_typer),
            (("minimal", "5"), with_typer),
            (("minimal", "5"), with_typer_app),
            (("minimal", "5"), with_typer_app),
            (("shellcompletion", "complete", "polls "), polls_with_typer),
            (("polls", "1"), polls_no_typer),
            (("polls", "2"), polls_with_typer),
        ]:
            run = RunKey(
                cmd=cmd[0],
                typer=not (
                    env is no_typer or env is polls_no_typer
                ),  # is this a typer command?
                app=env is with_typer_app
                or env is polls_with_typer,  # is django_typer in INSTALLED_APPS?
                rich=rich_installed,  # is rich installed?
                help=hlp,  # is this a help run?
            )
            if not run.typer and run.rich:
                continue  # no need for this combo

            # skip shellcompletion help
            if hlp and cmd[0] == "shellcompletion":
                continue

            if cmd[0] == "minimal":
                # sanity checks
                stats: t.Dict[str, t.Any] = run_command(
                    django_admin, "minimal", "5", "--print", **env
                )[0]  # type: ignore
                assert (
                    stats["app"] == "no_typer" if env is no_typer else "with_typer"
                ), "Wrong app detected"
                assert stats["test_arg"] == 5

            cmd = [django_admin, *cmd]
            if hlp:
                cmd.append("--help")
                run_command(*cmd, **env)  # make sure byte code is compiled

            import_trace(*cmd, **env)  # warm up
            imports = import_trace(
                *cmd,
                save=(
                    f"{run.cmd}_"
                    f"{'typer' if run.typer else 'base'}_"
                    f"{'app_' if run.app else ''}"
                    f"{'rich_' if run.rich else ''}"
                    f"{'help' if run.help else ''}.log"
                ),
                **env,
            )
            total_import_seconds = (
                float(sum([imprt[0] for imprt in imports.values()])) / 10**6
            )

            times = []
            for _ in range(run_counts):
                times.append(time_command(*cmd, **env)[-1])

            profile_data[pos_str]["runs"].setdefault(hash(run), {})
            profile_data[pos_str]["runs"][hash(run)] = {
                "run": run,
                "time": sum(times) / run_counts,
                "import_time": total_import_seconds,
                "modules": len(imports),
            }

    with open(profile_file, "w") as f:
        json.dump(profile_data, f, indent=4, default=dataclass_encoder)

    pprint(profile_data[pos_str])


@app.command(help="Update documentation to reflect latest profiling data.")
def document():
    if not rich_installed:
        raise typer.Exit("rich must be installed to run document")

    from rich import box
    from rich.console import Console
    from rich.table import Table
    from rich.text import Text

    profile = load()
    key = max((int(k) for k in profile.keys()))
    current = profile[str(key)]

    def to_str(ver):
        return ".".join((str(v) for v in ver))

    def minimal_table():
        console = Console(record=True, width=80)

        # Top "header"
        console.print(
            Text(
                f"{current['platform'].os} | {current['platform'].arch} | "
                f"Python {to_str(current['env'].python)}",
                style="bold magenta",
            ),
            justify="center",
        )
        console.print(
            Text(
                f"django-typer {to_str(current['env'].django_typer)} | Typer {to_str(current['env'].typer)}"
                f" | Django {to_str(current['env'].django)} ",
                style="dim",
            ),
            justify="center",
        )

        table = Table(
            show_header=True,
            box=box.SIMPLE_HEAVY,
            expand=True,
        )

        # Row-label column
        table.add_column("", style="bold white on grey23")

        no_rich_cols = [
            (
                "BaseCommand",
                RunKey(cmd="minimal", typer=False, app=False, rich=False, help=False),
            ),
            (
                "TyperCommand",
                RunKey(cmd="minimal", typer=True, app=True, rich=False, help=False),
            ),
        ]
        rich_cols = [
            (
                "TyperCommand (rich)",
                RunKey(cmd="minimal", typer=True, app=True, rich=True, help=False),
            ),
            (
                "TyperCommand --help (rich)",
                RunKey(cmd="minimal", typer=True, app=True, rich=True, help=True),
            ),
        ]

        no_rich_style = {
            "style": "black on light_goldenrod2",
            "header_style": "bold black on light_goldenrod2",
        }
        rich_style = {
            "style": "black on light_sky_blue1",
            "header_style": "bold black on light_sky_blue1",
        }
        for name, _ in no_rich_cols:
            table.add_column(name, justify="center", **no_rich_style)
        for name, _ in rich_cols:
            table.add_column(name, justify="center", **rich_style)

        for label, values in [
            (
                "modules",
                [
                    str(current["runs"][str(hash(key))]["modules"])
                    for _, key in (no_rich_cols + rich_cols)
                ],
            ),
            (
                "time",
                [
                    f"{current['runs'][str(hash(key))]['time']:.2f}"
                    for _, key in (no_rich_cols + rich_cols)
                ],
            ),
            (
                "imports",
                [
                    f"{current['runs'][str(hash(key))]['import_time']:.2f}"
                    for _, key in (no_rich_cols + rich_cols)
                ],
            ),
        ]:
            table.add_row(label, *values)

        console.print(table)

        svg = console.export_svg(title="CLI Startup Benchmarks")  # export as a string
        (
            Path(__file__).parent.parent / "doc/source/_static/img/minimal_profile.svg"
        ).write_text(svg, encoding="utf-8")

        console.print(table)

        svg = console.export_text()  # export as a string
        (
            Path(__file__).parent.parent / "doc/source/_static/img/minimal_profile.txt"
        ).write_text(svg, encoding="utf-8")

    def polls_table():
        console = Console(record=True, width=100)

        # Top "header"
        console.print(
            Text(
                f"{current['platform'].os} | {current['platform'].arch} | "
                f"Python {to_str(current['env'].python)}",
                style="bold magenta",
            ),
            justify="center",
        )
        console.print(
            Text(
                f"django-typer {to_str(current['env'].django_typer)} | Typer {to_str(current['env'].typer)}"
                f" | Django {to_str(current['env'].django)} ",
                style="dim",
            ),
            justify="center",
        )

        table = Table(
            show_header=True,
            box=box.SIMPLE_HEAVY,
            expand=True,
        )

        # Row-label column
        table.add_column("", style="bold white on grey23")

        no_rich_cols = [
            (
                "polls (tutorial)",
                RunKey(cmd="polls", typer=False, app=False, rich=False, help=False),
            ),
            (
                "polls --help (tutorial)",
                RunKey(cmd="polls", typer=False, app=False, rich=False, help=True),
            ),
            (
                "polls (typer)",
                RunKey(cmd="polls", typer=True, app=True, rich=False, help=False),
            ),
            (
                "shell completion",
                RunKey(
                    cmd="shellcompletion", typer=True, app=True, rich=False, help=False
                ),
            ),
        ]
        rich_cols = [
            (
                "polls (typer w/rich)",
                RunKey(cmd="polls", typer=True, app=True, rich=True, help=False),
            ),
            (
                "polls --help (typer w/rich)",
                RunKey(cmd="polls", typer=True, app=True, rich=True, help=True),
            ),
            (
                "shell completion (rich)",
                RunKey(
                    cmd="shellcompletion", typer=True, app=True, rich=True, help=False
                ),
            ),
        ]

        no_rich_style = {
            "style": "black on light_goldenrod2",
            "header_style": "bold black on light_goldenrod2",
        }
        rich_style = {
            "style": "black on light_sky_blue1",
            "header_style": "bold black on light_sky_blue1",
        }
        for name, _ in no_rich_cols:
            table.add_column(name, justify="center", **no_rich_style)
        for name, _ in rich_cols:
            table.add_column(name, justify="center", **rich_style)

        for label, values in [
            (
                "modules",
                [
                    str(current["runs"][str(hash(key))]["modules"])
                    for _, key in (no_rich_cols + rich_cols)
                ],
            ),
            (
                "time",
                [
                    f"{current['runs'][str(hash(key))]['time']:.2f}"
                    for _, key in (no_rich_cols + rich_cols)
                ],
            ),
            (
                "imports",
                [
                    f"{current['runs'][str(hash(key))]['import_time']:.2f}"
                    for _, key in (no_rich_cols + rich_cols)
                ],
            ),
        ]:
            table.add_row(label, *values)

        console.print(table)

        svg = console.export_svg(title="CLI Startup Benchmarks")  # export as a string
        (
            Path(__file__).parent.parent / "doc/source/_static/img/polls_profile.svg"
        ).write_text(svg, encoding="utf-8")

        console.print(table)
        svg = console.export_text()  # export as a string
        (
            Path(__file__).parent.parent / "doc/source/_static/img/polls_profile.txt"
        ).write_text(svg, encoding="utf-8")

    minimal_table()
    polls_table()


if __name__ == "__main__":
    app()  # type: ignore
