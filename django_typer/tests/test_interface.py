import typer
from django.test import TestCase

from django_typer import get_command, Typer, CommandGroup, AppFactory
from django_typer.tests.utils import get_named_arguments, get_named_defaults


class InterfaceTests(TestCase):
    """
    Make sure the django_typer decorator interfaces match the
    typer decorator interfaces. We don't simply pass variadic arguments
    to the typer decorator because we want the IDE to offer auto complete
    suggestions. This is a "developer experience" concession

    Include some other interface tests designed to test compatibility between
    the overrides and what the base class expects
    """

    def compare_defaults(
        self, params, dt_function, typer_function, require_placeholder_match=True
    ):
        if "cls" in params:
            params.remove(
                "cls"
            )  # cls default is always purposefully overriden in django-typer interfaces
        # sanity
        self.assertGreater(len(params), 0)
        dt_defaults = get_named_defaults(dt_function)
        typer_defaults = get_named_defaults(typer_function)
        count = 0
        for param in params:
            dt_default = dt_defaults[param]
            ty_default = typer_defaults[param]
            err_msg = f"param {param} does not mnatch between {dt_function}::{dt_default} and {typer_function}::{ty_default}"
            if isinstance(dt_default, typer.models.DefaultPlaceholder):
                if require_placeholder_match:
                    self.assertIsInstance(
                        ty_default, typer.models.DefaultPlaceholder, msg=err_msg
                    )
                dt_default = dt_default.value
            if isinstance(ty_default, typer.models.DefaultPlaceholder):
                # this will always fail out
                if require_placeholder_match:
                    self.assertIsInstance(
                        dt_defaults[param], typer.models.DefaultPlaceholder, msg=err_msg
                    )
                ty_default = ty_default.value
            self.assertEqual(dt_default, ty_default, msg=err_msg)
            count += 1
        return count

    def test_typer_command_interface_matches(self):
        dt_params = set(get_named_arguments(Typer.command))
        typer_params = set(get_named_arguments(typer.Typer.command))

        self.assertFalse(dt_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(dt_params, Typer.command, typer.Typer.command),
            len(dt_params),
        )

    def test_typer_callback_interface_matches(self):
        dt_params = set(get_named_arguments(Typer.callback))
        typer_params = set(get_named_arguments(typer.Typer.callback))

        self.assertFalse(dt_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(dt_params, Typer.callback, typer.Typer.callback),
            len(dt_params),
        )

    def test_typer_initialize_interface_matches(self):
        dt_params = set(get_named_arguments(Typer.initialize))
        typer_params = set(get_named_arguments(typer.Typer.callback))

        self.assertFalse(dt_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(dt_params, Typer.initialize, typer.Typer.callback),
            len(dt_params),
        )

    def test_typer_add_typer_interface_matches(self):
        dt_params = set(get_named_arguments(Typer.add_typer))
        typer_params = set(get_named_arguments(typer.Typer.add_typer))

        self.assertFalse(dt_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(dt_params, Typer.add_typer, typer.Typer.add_typer),
            len(dt_params),
        )

    def test_typer_init_interface_matches(self):
        dt_params = set(get_named_arguments(Typer.__init__))
        typer_params = set(get_named_arguments(typer.Typer.__init__))
        dt_params.remove("django_command")
        dt_params.remove("parent")
        self.assertFalse(dt_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(dt_params, Typer.__init__, typer.Typer.__init__),
            len(dt_params),
        )

    def test_commandgroup_init_interface_matches(self):
        dt_params = set(get_named_arguments(CommandGroup.__init__))
        typer_params = set(get_named_arguments(typer.Typer.__init__))
        if "django_command" in dt_params:
            dt_params.remove("django_command")
        dt_params.remove("parent")
        self.assertFalse(dt_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(
                dt_params, CommandGroup.__init__, typer.Typer.__init__
            ),
            len(dt_params),
        )

    def test_typer_metaclass_interface_matches(self):
        dt_params = set(get_named_arguments(AppFactory.__call__))
        typer_params = set(get_named_arguments(typer.Typer.__init__))
        if "django_command" in dt_params:
            dt_params.remove("django_command")
        if "parent" in dt_params:
            dt_params.remove("parent")
        self.assertFalse(dt_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(dt_params, AppFactory.__call__, typer.Typer.__init__),
            len(dt_params),
        )

    def test_command_interface_matches(self):
        from django_typer import command

        command_params = set(get_named_arguments(command))
        typer_params = set(get_named_arguments(typer.Typer.command))

        self.assertFalse(command_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(command_params, command, typer.Typer.command),
            len(command_params),
        )

    def test_group_interface_matches(self):
        from django_typer import group

        command_params = set(get_named_arguments(group))
        typer_params = set(get_named_arguments(typer.Typer.add_typer))
        typer_params.remove("callback")

        self.assertFalse(command_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(command_params, group, typer.Typer.add_typer),
            len(command_params),
        )

    def test_initialize_interface_matches(self):
        from django_typer import initialize

        initialize_params = set(get_named_arguments(initialize))
        typer_params = set(get_named_arguments(typer.Typer.callback))

        self.assertFalse(initialize_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(initialize_params, initialize, typer.Typer.callback),
            len(initialize_params),
        )

    def test_typercommandmeta_interface_matches(self):
        from django_typer import TyperCommandMeta

        typer_command_params = set(get_named_arguments(TyperCommandMeta.__new__))
        typer_params = set(get_named_arguments(typer.Typer.__init__))
        typer_params.remove("add_completion")
        self.assertFalse(typer_command_params.symmetric_difference(typer_params))

        typer_command_params.remove("pretty_exceptions_enable")
        typer_command_params.remove("pretty_exceptions_show_locals")
        typer_command_params.remove("pretty_exceptions_short")
        self.assertEqual(
            self.compare_defaults(
                typer_command_params, TyperCommandMeta.__new__, typer.Typer.__init__
            ),
            len(typer_command_params),
        )
        self.assertEqual(
            self.compare_defaults(
                [
                    "pretty_exceptions_enable",
                    "pretty_exceptions_show_locals",
                    "pretty_exceptions_short",
                ],
                TyperCommandMeta.__new__,
                typer.Typer.__init__,
                require_placeholder_match=False,
            ),
            3,
        )

    def test_commandgroup_group_interface_matches(self):
        from django_typer import CommandGroup

        typer_command_params = set(get_named_arguments(CommandGroup.group))
        typer_params = set(get_named_arguments(typer.Typer.add_typer))
        typer_params.remove("callback")
        self.assertFalse(typer_command_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(
                typer_command_params, CommandGroup.group, typer.Typer.add_typer
            ),
            len(typer_command_params),
        )

    def test_group_command_interface_matches(self):
        from django_typer import CommandGroup

        typer_command_params = set(get_named_arguments(CommandGroup.command))
        typer_params = set(get_named_arguments(typer.Typer.command))
        self.assertFalse(typer_command_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(
                typer_command_params, CommandGroup.command, typer.Typer.command
            ),
            len(typer_command_params),
        )

    def test_group_callback_interface_matches(self):
        from django_typer import CommandGroup

        typer_command_params = set(get_named_arguments(CommandGroup.callback))
        typer_params = set(get_named_arguments(typer.Typer.callback))
        self.assertFalse(typer_command_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(
                typer_command_params, CommandGroup.callback, typer.Typer.callback
            ),
            len(typer_command_params),
        )

    def test_base_class_command_interface_matches(self):
        from django_typer import TyperCommand

        command_params = set(get_named_arguments(TyperCommand.command))
        typer_params = set(get_named_arguments(typer.Typer.command))

        self.assertFalse(command_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(
                command_params, TyperCommand.command, typer.Typer.command
            ),
            len(command_params),
        )

    def test_base_class_group_interface_matches(self):
        from django_typer import TyperCommand

        command_params = set(get_named_arguments(TyperCommand.group))
        typer_params = set(get_named_arguments(typer.Typer.add_typer))
        typer_params.remove("callback")
        self.assertFalse(command_params.symmetric_difference(typer_params))
        self.assertEqual(
            self.compare_defaults(
                command_params, TyperCommand.group, typer.Typer.add_typer
            ),
            len(command_params),
        )

    def test_action_nargs(self):
        # unclear if nargs is even necessary - no other test seems to exercise it, leaving in for
        # base class compat reasons
        self.assertEqual(
            get_command("basic")
            .create_parser("./manage.py", "basic")
            ._actions[0]
            .nargs,
            1,
        )
        self.assertEqual(
            get_command("completion")
            .create_parser("./manage.py", "completion")
            ._actions[0]
            .nargs,
            -1,
        )
        multi_parser = get_command("multi").create_parser("./manage.py", "multi")
        self.assertEqual(multi_parser._actions[7].param.name, "files")
        self.assertEqual(multi_parser._actions[7].nargs, -1)
        self.assertEqual(multi_parser._actions[8].param.name, "flag1")
        self.assertEqual(multi_parser._actions[8].nargs, 0)
