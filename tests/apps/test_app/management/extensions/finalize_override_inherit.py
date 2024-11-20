from tests.apps.test_app.management.commands.finalize_override_inherit import (
    Command as FinalizeOverrideInherit,
)


@FinalizeOverrideInherit.finalize()
def ext_collect(self, result, **_):
    assert isinstance(self, FinalizeOverrideInherit)
    assert result == "handle"
    return "ext_collect: {}".format(result)
