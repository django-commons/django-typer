from django.test import TestCase

from tests.utils import run_command


class TestInheritance(TestCase):
    def test_handle_override(self):
        stdout, _, retcode = run_command("help_precedence8", "1", "2")
        self.assertEqual(retcode, 0)
        self.assertEqual(
            stdout,
            {
                "arg1": "1",
                "arg2": "2",
                "arg3": 0.5,
                "arg4": 1,
                "class": "<class 'tests.apps.test_app.management.commands.help_precedence8.Command'>",
            },
        )
        stdout, _, retcode = run_command("help_precedence16", "1", "2")
        self.assertEqual(retcode, 0)
        self.assertEqual(
            stdout,
            {
                "arg1": "1",
                "arg2": "2",
                "arg3": 0.5,
                "arg4": 1,
                "class": "<class 'tests.apps.test_app.management.commands.help_precedence16.Command'>",
            },
        )


class TestDiamondInheritance(TestCase):
    """
    Multiple inheritance works!! Even diamond inheritance!
    """

    def test_diamond_inheritance_run(self):
        stdout, _, retcode = run_command("inheritance3")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance2_1::init()" in stdout)

        stdout, _, retcode = run_command("inheritance3", "a")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance2_1::a()" in stdout)

        stdout, _, retcode = run_command("inheritance2_2", "a")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance2_2::a()" in stdout)

        stdout, _, retcode = run_command("inheritance3", "b")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance3::b()" in stdout)

        stdout, _, retcode = run_command("inheritance3", "c")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance2_2::c()" in stdout)

        stdout, _, retcode = run_command("inheritance3", "g2", "g2a")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance3::g2::g2a()" in stdout)

        stdout, _, retcode = run_command("inheritance1", "g")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance1::g()" in stdout)

        stdout, _, retcode = run_command("inheritance3", "g")
        self.assertGreater(retcode, 0)

        stdout, _, retcode = run_command("inheritance3", "g", "ga")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance2_1::g::ga()" in stdout)

        stdout, _, retcode = run_command("inheritance3", "g", "gb")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance2_1::g::gb()" in stdout)

        stdout, _, retcode = run_command("inheritance3", "g", "gc")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance2_1::g::gc()" in stdout)

        stdout, _, retcode = run_command("inheritance1", "g", "gc")
        self.assertGreater(retcode, 0)

        stdout, _, retcode = run_command("inheritance1", "g", "ga")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance1::g::ga()" in stdout)

        stdout, _, retcode = run_command("inheritance1", "g", "gb")
        self.assertEqual(retcode, 0)
        self.assertTrue("inheritance1::g::gb()" in stdout)
