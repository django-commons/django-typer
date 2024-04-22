from django.test import TestCase

from django_typer import TyperCommand, group


class CommandDefinitionTests(TestCase):
    def test_group_callback_throws(self):
        class CBTestCommand(TyperCommand):
            @group()
            def grp():
                pass

            grp.group()

            def grp2():
                pass

        with self.assertRaises(NotImplementedError):

            class CommandBad(TyperCommand):
                @group()
                def grp():
                    pass

                @grp.callback()
                def bad_callback():
                    pass

        with self.assertRaises(NotImplementedError):

            class CommandBad(CBTestCommand):
                @CBTestCommand.grp.callback()
                def bad_callback():
                    pass
