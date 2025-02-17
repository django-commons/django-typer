from tests.apps.test_app.management.commands.finalize_subgroups_inherit import (
    Command as FinalizeSubgroupsInherit,
)


# test that we can override a finalize method from a parent class
@FinalizeSubgroupsInherit.grp1.finalize()
def grp1_collect(self, result, **kwargs):
    assert isinstance(self, FinalizeSubgroupsInherit)
    return f"grp1_collect: {self.grp1_final(result, **kwargs)}"


@FinalizeSubgroupsInherit.grp2.finalize()
def grp2_collect(result, **kwargs):
    return f"grp2_collect: {FinalizeSubgroupsInherit.grp2_final(result, **kwargs)}"


@FinalizeSubgroupsInherit.grp1.command()
def cmd5(self):
    return "cmd5"
