from django_typer.utils import called_from_module, called_from_command_definition

print(called_from_module())
print(called_from_module(look_back=0))
print(called_from_module(look_back=3))


def function():
    print(called_from_module())


def nested():
    def nested2():
        print(called_from_module())

    nested2()


class Command:
    called_from_defn = called_from_command_definition(look_back=0)


function()
nested()

print(Command.called_from_defn)
