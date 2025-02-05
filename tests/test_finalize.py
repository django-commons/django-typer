import contextlib
from io import StringIO

from django.core.management import call_command
from django.test import TestCase

from django_typer.management import get_command
from tests.utils import run_command, rich_installed


class TestFinalize(TestCase):
    def test_finalize_multi_kwargs_run(
        self, command="finalize_multi_kwargs", show_locals=rich_installed
    ):
        stdout, _, _ = run_command(command, "cmd1")
        self.assertEqual(
            stdout.strip(),
            "finalized: ['cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False, 'show_locals': None}"
            if show_locals
            else "finalized: ['cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False}",
        )
        stdout, _, _ = run_command(command, "cmd2", "3", "cmd1")
        self.assertEqual(
            stdout.strip(),
            "finalized: ['cmd2 3', 'cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False, 'show_locals': None}"
            if show_locals
            else "finalized: ['cmd2 3', 'cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False}",
        )

    def test_finalize_multi_named_param_run(self):
        self.test_finalize_multi_kwargs_run(
            command="finalize_multi_named_param", show_locals=True
        )

    def test_finalize_no_params_run(self):
        stdout, _, _ = run_command("finalize_multi_no_params", "cmd1")
        self.assertEqual(
            stdout.strip(),
            "finalized: ['cmd1 1']",
        )

        stdout, _, _ = run_command("finalize_multi_no_params", "cmd2", "3", "cmd1")
        self.assertEqual(
            stdout.strip(),
            "finalized: ['cmd2 3', 'cmd1 1']",
        )

    def test_finalize_multi_kwargs_call(
        self, command="finalize_multi_kwargs", show_locals=rich_installed
    ):
        # todo - excluded common options should not appear?
        call_command(command, "cmd1")
        with contextlib.redirect_stdout(StringIO()) as out:
            call_command(command, "cmd1")
            self.assertEqual(
                out.getvalue().strip(),
                "finalized: ['cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False, 'show_locals': None}"
                if show_locals
                else "finalized: ['cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False}",
            )

            out.truncate(0)
            out.seek(0)

            call_command(command, "cmd2", "5", "cmd1")
            self.assertEqual(
                out.getvalue().strip(),
                "finalized: ['cmd2 5', 'cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False, 'show_locals': None}"
                if show_locals
                else "finalized: ['cmd2 5', 'cmd1 1'] | {'force_color': False, 'no_color': False, 'traceback': False}",
            )

            out.truncate(0)
            out.seek(0)

            call_command(
                command,
                "--traceback",
                "cmd2",
                "3",
                "cmd1",
                "--arg1",
                "2",
            )
            self.assertEqual(
                out.getvalue().strip(),
                "finalized: ['cmd2 3', 'cmd1 2'] | {'force_color': False, 'no_color': False, 'traceback': True, 'show_locals': None}"
                if show_locals
                else "finalized: ['cmd2 3', 'cmd1 2'] | {'force_color': False, 'no_color': False, 'traceback': True}",
            )

    def test_finalize_multi_named_param_call(self):
        self.test_finalize_multi_kwargs_call(
            command="finalize_multi_named_param", show_locals=True
        )

    def test_finalize_multi_no_params(self):
        # todo - excluded common options should not appear?
        call_command("finalize_multi_no_params", "cmd1")
        with contextlib.redirect_stdout(StringIO()) as out:
            call_command("finalize_multi_no_params", "cmd1")
            self.assertEqual(
                out.getvalue().strip(),
                "finalized: ['cmd1 1']",
            )

            out.truncate(0)
            out.seek(0)

            call_command("finalize_multi_no_params", "cmd2", "5", "cmd1")
            self.assertEqual(
                out.getvalue().strip(),
                "finalized: ['cmd2 5', 'cmd1 1']",
            )

            out.truncate(0)
            out.seek(0)

            call_command(
                "finalize_multi_no_params",
                "--traceback",
                "cmd2",
                "3",
                "cmd1",
                "--arg1",
                "2",
            )
            self.assertEqual(
                out.getvalue().strip(),
                "finalized: ['cmd2 3', 'cmd1 2']",
            )

    def test_finalize_multi_kwargs_obj(
        self, command="finalize_multi_kwargs", kwargs=""
    ):
        from tests.apps.test_app.management.commands.finalize_multi_kwargs import (
            Command,
        )

        out = StringIO()
        finalize4 = get_command(command, Command, stdout=out)
        self.assertEqual(
            finalize4.final([finalize4.cmd1(3), finalize4.cmd2(2)]).strip(),
            f"finalized: ['cmd1 3', 'cmd2 2'] | {{{kwargs}}}",
        )

    def test_finalize_multi_named_param_obj(self):
        self.test_finalize_multi_kwargs_obj(
            command="finalize_multi_named_param",
            kwargs="'force_color': None, 'no_color': None, 'traceback': None, 'show_locals': None",
        )

    def test_finalize_multi_no_params_obj(
        self, command="finalize_multi_no_params", kwargs=""
    ):
        from tests.apps.test_app.management.commands.finalize_multi_no_params import (
            Command,
        )

        out = StringIO()
        finalize_multi_no_params = get_command(command, Command, stdout=out)
        self.assertEqual(
            finalize_multi_no_params.final(
                [finalize_multi_no_params.cmd1(3), finalize_multi_no_params.cmd2(2)]
            ).strip(),
            f"finalized: ['cmd1 3', 'cmd2 2']",
        )

    def test_finalize_simple_run(self):
        stdout, _, _ = run_command("finalize_simple")
        self.assertEqual(stdout.strip(), "finalized: handle")

    def test_finalize_simple_call(self):
        out = StringIO()
        call_command("finalize_simple", stdout=out)
        self.assertEqual(out.getvalue().strip(), "finalized: handle")

    def test_finalize_simple_obj(self):
        from tests.apps.test_app.management.commands.finalize_simple import Command

        out = StringIO()
        finalize_simple = get_command("finalize_simple", Command, stdout=out)
        self.assertEqual(
            finalize_simple.final(finalize_simple()).strip(),
            "finalized: handle",
        )

    def test_finalize_static_run(self):
        stdout, _, _ = run_command("finalize_static")
        self.assertEqual(stdout.strip(), "finalized: handle | traceback=False")

        stdout, _, _ = run_command("finalize_static", "--traceback")
        self.assertEqual(stdout.strip(), "finalized: handle | traceback=True")

    def test_finalize_static_call(self):
        out = StringIO()
        call_command("finalize_static", stdout=out)
        self.assertEqual(out.getvalue().strip(), "finalized: handle | traceback=False")

        out = StringIO()
        call_command("finalize_static", traceback=True, stdout=out)
        self.assertEqual(out.getvalue().strip(), "finalized: handle | traceback=True")

    def test_finalize_static_obj(self):
        from tests.apps.test_app.management.commands.finalize_static import Command

        out = StringIO()
        finalize_static = get_command("finalize_static", Command, stdout=out)
        self.assertEqual(
            finalize_static.final(finalize_static()).strip(),
            "finalized: handle | traceback=False",
        )

    def test_finalize_subgroups_run(self):
        stdout, _, _ = run_command("finalize_subgroups", "grp2", "cmd4", "cmd3")
        self.assertEqual(
            stdout.strip(),
            "root_final: grp2_final: ['cmd4', 'cmd3'] | g2_opt=True | init_opt=False",
        )

        stdout, _, _ = run_command(
            "finalize_subgroups", "--init-opt", "grp2", "--no-g2-opt", "cmd3"
        )
        self.assertEqual(
            stdout.strip(),
            "root_final: grp2_final: ['cmd3'] | g2_opt=False | init_opt=True",
        )

        stdout, _, _ = run_command(
            "finalize_subgroups", "--init-opt", "grp1", "--no-g1-opt", "cmd2", "cmd2"
        )
        self.assertEqual(
            stdout.strip(),
            "root_final: grp1_final: ['cmd2', 'cmd2'] | g1_opt=False | init_opt=True",
        )

        stdout, _, _ = run_command("finalize_subgroups", "grp1", "cmd2", "cmd1")
        self.assertEqual(
            stdout.strip(),
            "root_final: grp1_final: ['cmd2', 'cmd1'] | g1_opt=False | init_opt=False",
        )

    def test_finalize_subgroups_call(self):
        out = StringIO()
        call_command(
            "finalize_subgroups", "grp2", "cmd4", "cmd3", stdout=out, call_command=True
        )
        self.assertEqual(
            out.getvalue().strip(),
            "root_final: grp2_final: ['cmd4', 'cmd3'] | g2_opt=True | init_opt=False",
        )

        out = StringIO()
        call_command(
            "finalize_subgroups",
            "grp2",
            "cmd3",
            init_opt=True,
            g2_opt=False,
            stdout=out,
            call_command=True,
        )
        self.assertEqual(
            out.getvalue().strip(),
            "root_final: grp2_final: ['cmd3'] | g2_opt=False | init_opt=True",
        )

        out = StringIO()
        call_command(
            "finalize_subgroups",
            "grp1",
            "--no-g1-opt",
            "cmd2",
            "cmd2",
            init_opt=True,
            stdout=out,
            call_command=True,
        )
        self.assertEqual(
            out.getvalue().strip(),
            "root_final: grp1_final: ['cmd2', 'cmd2'] | g1_opt=False | init_opt=True",
        )

        out = StringIO()
        call_command(
            "finalize_subgroups", "grp1", "cmd2", "cmd1", stdout=out, call_command=True
        )
        self.assertEqual(
            out.getvalue().strip(),
            "root_final: grp1_final: ['cmd2', 'cmd1'] | g1_opt=False | init_opt=False",
        )

    def test_finalize_subgroups_obj(self):
        from tests.apps.test_app.management.commands.finalize_subgroups import Command

        out = StringIO()
        finalize_subgroups = get_command("finalize_subgroups", Command, stdout=out)
        finalize_subgroups.init(init_opt=True, direct_call=True)
        self.assertEqual(
            finalize_subgroups.root_final(
                [
                    finalize_subgroups.grp1_final(
                        [
                            finalize_subgroups.grp1.cmd2(),
                            finalize_subgroups.grp1.cmd2(),
                        ]
                    )
                ],
                init_opt=True,
            ).strip(),
            "root_final: [\"grp1_final: ['cmd2', 'cmd2'] | g1_opt=None\"] | init_opt=True",
        )

        self.assertEqual(
            finalize_subgroups.root_final(
                [
                    finalize_subgroups.grp1.grp1_final(
                        [
                            finalize_subgroups.cmd1(),
                            finalize_subgroups.cmd2(),
                        ]
                    )
                ],
                init_opt=False,
            ).strip(),
            "root_final: [\"grp1_final: ['cmd1', 'cmd2'] | g1_opt=None\"] | init_opt=False",
        )
        self.assertEqual(
            finalize_subgroups.root_final(
                [
                    finalize_subgroups.grp2.grp2_final(
                        [
                            finalize_subgroups.cmd3(),
                            finalize_subgroups.cmd4(),
                        ],
                        g2_opt=False,
                    )
                ],
                init_opt=False,
            ).strip(),
            "root_final: [\"grp2_final: ['cmd3', 'cmd4'] | g2_opt=False\"] | init_opt=False",
        )

    def test_finalize_override_run(self):
        stdout, _, _ = run_command("finalize_override")
        self.assertEqual(stdout.strip(), "collect: handle")

    def test_finalize_override_call(self):
        out = StringIO()
        call_command("finalize_override", stdout=out)
        self.assertEqual(out.getvalue().strip(), "collect: handle")

    def test_finalize_override_obj(self):
        from tests.apps.test_app.management.commands.finalize_override import Command

        out = StringIO()
        finalize_override = get_command("finalize_override", Command, stdout=out)
        self.assertEqual(
            finalize_override.collect(finalize_override()).strip(),
            "collect: handle",
        )
        self.assertEqual(
            finalize_override.final(finalize_override()).strip(),
            "finalized: handle",
        )

    def test_finalize_override_inherit_run(self):
        stdout, _, _ = run_command("finalize_override_inherit")
        self.assertEqual(stdout.strip(), "ext_collect: handle")

    def test_finalize_override_inherit_call(self):
        out = StringIO()
        call_command("finalize_override_inherit", stdout=out)
        self.assertEqual(out.getvalue().strip(), "ext_collect: handle")

    def test_finalize_override_inherit_obj(self):
        from tests.apps.test_app.management.commands.finalize_override_inherit import (
            Command,
        )

        out = StringIO()
        finalize_override = get_command(
            "finalize_override_inherit", Command, stdout=out
        )
        self.assertEqual(
            finalize_override.ext_collect(finalize_override()).strip(),
            "ext_collect: handle",
        )
        self.assertEqual(
            finalize_override.final(finalize_override()).strip(),
            "finalized: handle",
        )

    def test_finalize_subgroups_inherit_run(self):
        stdout, _, _ = run_command("finalize_subgroups_inherit", "grp2", "cmd4", "cmd3")
        self.assertEqual(
            stdout.strip(),
            "root_final: grp2_collect: grp2_final: ['cmd4', 'cmd3'] | g2_opt=True | init_opt=False",
        )

        stdout, _, _ = run_command(
            "finalize_subgroups_inherit", "--init-opt", "grp2", "--no-g2-opt", "cmd3"
        )
        self.assertEqual(
            stdout.strip(),
            "root_final: grp2_collect: grp2_final: ['cmd3'] | g2_opt=False | init_opt=True",
        )

        stdout, _, _ = run_command(
            "finalize_subgroups_inherit",
            "--init-opt",
            "grp1",
            "--no-g1-opt",
            "cmd2",
            "cmd2",
        )
        self.assertEqual(
            stdout.strip(),
            "root_final: grp1_collect: grp1_final: ['cmd2', 'cmd2'] | g1_opt=False | init_opt=True",
        )

        stdout, _, _ = run_command("finalize_subgroups_inherit", "grp1", "cmd2", "cmd1")
        self.assertEqual(
            stdout.strip(),
            "root_final: grp1_collect: grp1_final: ['cmd2', 'cmd1'] | g1_opt=False | init_opt=False",
        )

    def test_finalize_subgroups_inherit_call(self):
        out = StringIO()
        call_command(
            "finalize_subgroups_inherit",
            "grp2",
            "cmd4",
            "cmd3",
            stdout=out,
            call_command=True,
        )
        self.assertEqual(
            out.getvalue().strip(),
            "root_final: grp2_collect: grp2_final: ['cmd4', 'cmd3'] | g2_opt=True | init_opt=False",
        )

        out = StringIO()
        call_command(
            "finalize_subgroups_inherit",
            "grp2",
            "cmd3",
            init_opt=True,
            g2_opt=False,
            stdout=out,
            call_command=True,
        )
        self.assertEqual(
            out.getvalue().strip(),
            "root_final: grp2_collect: grp2_final: ['cmd3'] | g2_opt=False | init_opt=True",
        )

        out = StringIO()
        call_command(
            "finalize_subgroups_inherit",
            "grp1",
            "--no-g1-opt",
            "cmd2",
            "cmd2",
            init_opt=True,
            stdout=out,
            call_command=True,
        )
        self.assertEqual(
            out.getvalue().strip(),
            "root_final: grp1_collect: grp1_final: ['cmd2', 'cmd2'] | g1_opt=False | init_opt=True",
        )

        out = StringIO()
        call_command(
            "finalize_subgroups_inherit",
            "grp1",
            "cmd2",
            "cmd1",
            stdout=out,
            call_command=True,
        )
        self.assertEqual(
            out.getvalue().strip(),
            "root_final: grp1_collect: grp1_final: ['cmd2', 'cmd1'] | g1_opt=False | init_opt=False",
        )

    def test_finalize_subgroups_inherit_obj(self):
        from tests.apps.test_app.management.commands.finalize_subgroups_inherit import (
            Command,
        )

        out = StringIO()
        finalize_subgroups = get_command(
            "finalize_subgroups_inherit", Command, stdout=out
        )
        finalize_subgroups.init(init_opt=True, direct_call=True)
        self.assertEqual(finalize_subgroups.cmd5(), "cmd5")
        self.assertEqual(
            finalize_subgroups.root_final(
                [
                    finalize_subgroups.grp1_collect(
                        [
                            finalize_subgroups.grp1.cmd2(),
                            finalize_subgroups.grp1.cmd2(),
                        ]
                    )
                ],
                init_opt=True,
            ).strip(),
            "root_final: [\"grp1_collect: grp1_final: ['cmd2', 'cmd2'] | g1_opt=None\"] | init_opt=True",
        )

        self.assertEqual(
            finalize_subgroups.root_final(
                [
                    finalize_subgroups.grp1.grp1_collect(
                        [
                            finalize_subgroups.cmd1(),
                            finalize_subgroups.cmd2(),
                        ]
                    )
                ],
                init_opt=False,
            ).strip(),
            "root_final: [\"grp1_collect: grp1_final: ['cmd1', 'cmd2'] | g1_opt=None\"] | init_opt=False",
        )
        self.assertEqual(
            finalize_subgroups.root_final(
                [
                    finalize_subgroups.grp2.grp2_final(
                        [
                            finalize_subgroups.cmd3(),
                            finalize_subgroups.cmd4(),
                        ],
                        g2_opt=False,
                    )
                ],
                init_opt=False,
            ).strip(),
            "root_final: [\"grp2_collect: grp2_final: ['cmd3', 'cmd4'] | g2_opt=False\"] | init_opt=False",
        )
