import contextlib
from io import StringIO

from django.core.management import call_command
from django.test import TestCase
from django.utils import timezone
import contextlib

from django_typer.management import get_command
from tests.apps.examples.polls.models import Question

SHELLS = [("zsh", True), ("bash", False), ("pwsh", True), ("fish", True)]


class TestPollExample(TestCase):
    q1 = None
    q2 = None
    q3 = None

    databases = {"default"}

    typer = ""

    def setUp(self):
        self.q1 = Question.objects.create(
            question_text="Is Putin a war criminal?",
            pub_date=timezone.now(),
        )
        self.q2 = Question.objects.create(
            question_text="Is Bibi a war criminal?",
            pub_date=timezone.now(),
        )
        self.q3 = Question.objects.create(
            question_text="Is Xi a Pooh Bear?",
            pub_date=timezone.now(),
        )
        super().setUp()

    def tearDown(self):
        Question.objects.all().delete()
        super().tearDown()

    def test_poll_complete(self):
        # result = run_command("shellcompletion", "complete", "./manage.py closepoll ")

        for shell, has_help in SHELLS:
            result1 = StringIO()
            with contextlib.redirect_stdout(result1):
                call_command(
                    "shellcompletion",
                    "complete",
                    shell=shell,
                    command=f"closepoll{self.typer} ",
                )
            result2 = StringIO()
            with contextlib.redirect_stdout(result2):
                call_command(
                    "shellcompletion",
                    "complete",
                    shell=shell,
                    command=f"./manage.py closepoll{self.typer} ",
                )

            result = result1.getvalue()
            self.assertEqual(result, result2.getvalue())
            for q in [self.q1, self.q2, self.q3]:
                self.assertTrue(str(q.id) in result)
                if has_help:
                    self.assertTrue(q.question_text in result)

    def test_tutorial1(self):
        with contextlib.redirect_stdout(StringIO()) as output:
            call_command(f"closepoll_t1{self.typer}", str(self.q2.id))
            result = output.getvalue()
        self.assertEqual(result.strip(), f'Successfully closed poll "{self.q2.id}"')

    def test_tutorial2(self):
        with contextlib.redirect_stdout(StringIO()) as output:
            call_command(f"closepoll_t2{self.typer}", str(self.q2.id))
            result = output.getvalue()
        self.assertEqual(result.strip(), f'Successfully closed poll "{self.q2.id}"')

    def test_tutorial_parser(self):
        with contextlib.redirect_stdout(StringIO()) as output:
            call_command(f"closepoll_t3{self.typer}", str(self.q1.id))
            result = output.getvalue()
        self.assertEqual(result.strip(), f'Successfully closed poll "{self.q1.id}"')

    def test_tutorial_parser_cmd(self):
        log = StringIO()
        call_command(f"closepoll_t3{self.typer}", str(self.q1.id), stdout=log)
        cmd = get_command(f"closepoll_t3{self.typer}", stdout=log)
        cmd([self.q1])
        cmd(polls=[self.q1])
        # these don't work, maybe revisit in future?
        # cmd([str(self.q1.id)])
        # cmd([self.q1.id])
        self.assertEqual(log.getvalue().count("Successfully"), 3)

    def test_tutorial_modelobjparser_cmd(self):
        log = StringIO()
        call_command(f"closepoll_t6{self.typer}", str(self.q1.id), stdout=log)
        cmd = get_command(f"closepoll_t6{self.typer}", stdout=log)
        cmd([self.q1])
        cmd(polls=[self.q1])
        self.assertEqual(log.getvalue().count("Successfully"), 3)

    def test_poll_ex(self):
        with contextlib.redirect_stdout(StringIO()) as output:
            call_command(f"closepoll{self.typer}", str(self.q2.id))
            result = output.getvalue()
        self.assertTrue("Successfully closed poll" in result)


class TestPollExampleTyper(TestPollExample):
    typer = "_typer"
