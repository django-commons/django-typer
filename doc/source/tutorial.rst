.. include:: ./refs.rst

========
Tutorial
========

Using TyperCommands is very similar to using BaseCommands. The main difference is that you use
Typer_'s decorators, classes and type annotations to define the command's command line interface
instead of argparse_.

For this tutorial we will be building off the 
`polls example in the Django documentation <https://docs.djangoproject.com/en/stable/howto/custom-management-commands/#module-django.core.management>`_.
Please first work through this tutorial to see how defining the below TyperCommand differs.


