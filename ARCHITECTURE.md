# Architecture

The principal design challenge of [django-typer](https://pypi.python.org/pypi/django-typer) is to manage the [Typer](https://typer.tiangolo.com/) app trees associated with each Django management command class and to keep these trees separate when classes are inherited and allow them to be edited directly when commands are extended through the plugin pattern. There are also incurred complexities with adding default django options where appropriate and supporting command callbacks as methods or static functions. Supporting dynamic command/group access through attributes on command instances also requires careful usage of esoteric Python features.

The [Typer](https://typer.tiangolo.com/) app tree defines the layers of groups and commands that define the CLI. Each [TyperCommand](https://django-typer.readthedocs.io/en/latest/reference.html#django_typer.TyperCommand) maintains its own app tree defined by a root [Typer](https://django-typer.readthedocs.io/en/latest/reference.html#django_typer.management.Typer) node. When other classes inherit from a base command class, that app tree is copied and the new class can modify it without affecting the base class's tree. We extend [Typer](https://typer.tiangolo.com/)'s Typer type with our own [Typer](https://django-typer.readthedocs.io/en/latest/reference.html#django_typer.management.Typer) class that adds additional bookkeeping and attribute resolution features we need.

[django-typer](https://pypi.python.org/pypi/django-typer) must behave intuitively as expected and therefore it must support all of the following:

* Inherited classes can extend and override groups and commands defined on the base class without affecting the base class so that the base class may still be imported and used directly as it was originally designed.
* Extensions defined using the plugin pattern must be able to modify the app trees of the commands they plugin to directly.
* The group/command tree on instantiated commands must be walkable using attributes from the command instance itself to support subgroup name overloads.
* Common django options should appear on the initializer for compound commands and should be directly on the command for non-compound commands.

During all of this, the correct self must be passed if the function accepts it, but all of the registered functions are not registered as methods because they enter the [Typer](https://typer.tiangolo.com/) app tree as regular functions. This means another thing [django-typer](https://pypi.python.org/pypi/django-typer) must do is decide if a function is a method and if so, bind it to the correct class and pass the correct self instance. The method test is [is_method](https://django-typer.readthedocs.io/en/latest/reference.html#django_typer.utils.is_method) and simply checks to see if the function accepts a first positional argument named `self`.

[django-typer](https://pypi.python.org/pypi/django-typer) uses metaclasses to build the typer app tree when [TyperCommand](https://django-typer.readthedocs.io/en/latest/reference.html#django_typer.TyperCommand) classes are instantiated. The logic flow proceeds this way:

- Class definition is read and @initialize/@callback, @group, @command decorators label and store typer config and registration logic onto the function objects for processing later once the root [Typer](https://typer.tiangolo.com/) app is created.
- Metaclass __new__ creates the root [Typer](https://typer.tiangolo.com/) app for the class and redirects the implementation of handle if it exists. It then walks the classes in MRO order and runs the cached command/group registration logic for commands and groups defined directly on each class. Commands and groups defined dynamically (i.e. registered after Command class definition in plugins) *are not* included during this registration because they do not appear as attributes on the base classes. This keeps inheritance pure while allowing plugins to not interfere. The exception to this is when using the Typer-style interface where all commands and groups are registered dynamically. A [Typer](https://django-typer.readthedocs.io/en/latest/reference.html#django_typer.management.Typer) instance is passed as an argument to the [Typer](https://django-typer.readthedocs.io/en/latest/reference.html#django_typer.management.Typer) constructor and when this happens, the commands and groups will be copied.
- Metaclass __init__ sets the newly created Command class into the typer app tree and determines if a common initializer needs to be added containing the default unsupressed django options.
- Command __init__ loads any registered plugins (this is a one time opperation that will happen when the first Command of a given type is instantiated). It also determines if the addition of any plugins should necessitate the addition of a common initializer and makes some last attempts to pick the correct help from __doc__ if no help is present.

Below you can see that the backup inheritance example [Typer](https://django-typer.readthedocs.io/en/latest/reference.html#django_typer.management.Typer) tree. Each command class has its own completely separate tree.

![Inheritance Tree](https://raw.githubusercontent.com/bckohan/django-typer/main/doc/source/_static/img/inheritance_tree.png)

Contrast this with the backup plugin example where after the plugins are loaded the same command tree has been altered. Note that after the plugins have been applied two database commands are present. This is ok, the ones added last will be used.

![Plugin Tree](https://raw.githubusercontent.com/bckohan/django-typer/main/doc/source/_static/img/plugin_tree.png)

```python

    class Command(TyperCommand):

        # command() runs before the Typer app is created, therefore we
        # have to cache it and run it later during class creation
        @command()
        def cmd1(self):
            pass

        @group()
        def grp1(self):
            pass

        @grp1.group(self):
        def grp2(self):
            pass
```

```python

    class Command(UpstreamCommand):

      # This must *not* alter the grp1 app on the base
      # app tree but instead create a new one on this
      # commands app tree when it is created
      @UpstreamCommand.grp1.command()
      def cmd3(self):
          pass

      # this gets interesting though, because these should be
      # equivalent:
      @UpstreamCommand.grp2.command()
      def cmd4(self):
          pass

      # we use custom __getattr__ methods on TyperCommand and Typer to
      # dynamically run BFS search for command and groups if the members
      # are not present on the command definition.
      @UpstreamCommand.grp1.grp2.command()
      def cmd4(self):
          pass
```

```python

  # extensions called at module scope should modify the app tree of the
  # command directly
  @UpstreamCommand.grp1.command()
  def cmd4(self):
      pass

```

```python

  app = Typer()

  # similar to extensions these calls should modify the app tree directly
  # the Command class exists after the first Typer() call and app is a reference
  # directly to Command.typer_app
  @app.callback()
  def init():
    pass


  @app.command()
  def main():
      pass

  grp2 = Typer()
  app.add_typer(grp2)

  @grp2.callback(name="grp1")
  def init_grp1():
      pass

  @grp2.command()
  def cmd2():
      pass

```

## Notes on [BaseCommand](https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#django.core.management.BaseCommand)

There are a number of encumbrances in the Django management command design that make our implementation more difficult than it need be. We document them here mostly to keep track of them for potential future core Django work.

  1) BaseCommand::execute() prints results to stdout without attempting to convert them
     to strings. This means you've gotta do weird stuff to get a return object out of
     call_command()

  2) call_command() converts arguments to strings. There is no official way to pass
     previously parsed arguments through call_command(). This makes it a bit awkward to
     use management commands as callable functions in django code which you should be able
     to easily do. django-typer allows you to invoke the command and group functions
     directly so you can work around this, but it would be nice if call_command() supported
     a general interface that all command libraries could easily implement to.

  3) terminal autocompletion is not pluggable. As of this writing (Django<=5)
     autocomplete is implemented for bash only and has no mechanism for passing the buck
     down to command implementations. The result of this in django-typer is that we wrap
     django's autocomplete and pass the buck to it instead of the other way around. This is
     fine but it will be awkward if two django command line apps with their own autocomplete
     infrastructure are used together. Django should be the central coordinating point for
     this. This is the reason for the pluggable --fallback awkwardness in shellcompletion.

  4) Too much of the BaseCommand implementation is built assuming argparse. A more
     generalized abstraction of this interface is in order. Right now BaseCommand is doing
     double duty both as a base class and a protocol.

  5) There is an awkwardness to how parse_args flattens all the arguments and options
     into a single dictionary. This means that when mapping a library like Typer onto the
     BaseCommand interface you cannot allow arguments at different levels
     (e.g. in initialize()) or group() functions above the command to have the same names as
     the command's options. You can work around this by using a different name for the
     option in the command and supplying the desired name in the annotation, but its an odd
     quirk imposed by the base class for users to be aware of.
