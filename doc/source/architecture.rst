.. include:: ./refs.rst

Architecture
------------

The principal design challenge of django-typer_ is to manage the Typer_ app trees associated with
each Django management command class and to keep these trees separate when classes are inherited
and allow them to be edited directly when commands are extended through the composition pattern.

The Typer_ app tree defines the layers of groups and commands that define the CLI. Each
:class:`~django_typer.TyperCommand` maintains its own app tree, and when other classes inherit from
a base command class, that app tree is copied and the new class can modify it without affecting the
base class.

django-typer_ must support all of the following:

* Inherited classes can extend and override groups and commands defined on the base class without
  affecting the base class so that the base class may still be imported and used directly as it
  was originally designed.
* Extensions defined using the composition pattern must be able to modify the app trees of the
  commands they extend directly.
* The group/command tree on instantiated commands must be walkable using attributes from the
  command instance itself to support subgroup name overloads.

During all of this, the correct self must be passed if the function accepts it, but all of the
registered functions are not registered as methods because they enter the Typer_ app tree as
regular functions. This means another thing django-typer_ must do is decide if a function is a
method and if so, bind it to the correct class and pass the correct self instance. The method
test is :func:`~django_typer.utils.is_method` and simply checks to see if the function accepts
a first positional argument named `self`.

django-typer_ uses metaclasses to build the typer app tree when :class:`~django_typer.TyperCommand`
classes are instantiated. The logic flow proceeds this way:

- Class definition is read and @initialize, @group, @command decorators label and store typer
  config and registration logic onto the function objects for processing later once the root
  Typer_ app is created.
- Metaclass __new__ creates the root Typer_ app for the class and caches the implementation of
  handle if it exists.
- Metaclass __init__ walks the class tree and copies the Typer_ app tree from the parent class
  to the child class.



.. code-block:: python

    class Command(TyperCommand):

        # command() runs before the Typer_ app is created, therefore we
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


.. code-block:: python

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

      @UpstreamCommand.grp1.grp2.command()
      def cmd4(self):
          pass


.. code-block:: python

  # extensions called at module scope should modify the app tree of the
  # command directly
  @UpstreamCommand.grp1.command()
  def cmd4(self):
      pass


.. code-block:: python

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
