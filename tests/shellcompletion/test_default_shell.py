import pytest
from django.core.management import CommandError
from django.test import TestCase

from tests.shellcompletion import _DefaultCompleteTestCase, default_shell


@pytest.mark.skipif(default_shell is None, reason="shellingham failed to detect shell")
class DefaultCompleteTestCase(_DefaultCompleteTestCase, TestCase):
    pass


@pytest.mark.skipif(default_shell is not None, reason="shellingham detected a shell")
class DefaultCompleteFailTestCase(_DefaultCompleteTestCase, TestCase):
    def setUp(self):
        TestCase.setUp(self)

    def tearDown(self):
        TestCase.tearDown(self)

    def test_shell_complete(self):
        with self.assertRaises(CommandError):
            self.install()
