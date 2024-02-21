from datetime import datetime
import sys
import os
from pathlib import Path
from sphinx.ext.autodoc import between
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_typer.tests.settings')
django.setup()

sys.path.append(str(Path(__file__).parent / 'django_typer' / 'examples'))
sys.path.append(str(Path(__file__).parent / 'django_typer' / 'tests'))
import django_typer

# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.
#
# import os
# import sys
# sys.path.insert(0, os.path.abspath('.'))


# -- Project information -----------------------------------------------------

project = 'django_typer'
copyright = f'2023-{datetime.now().year}, Brian Kohan'
author = 'Brian Kohan'

# The full version, including alpha/beta/rc tags
release = django_typer.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx_rtd_theme',
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinxcontrib.typer'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = []


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
#
html_theme = 'sphinx_rtd_theme'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = [
    '_static',
]
html_css_files = [
    'style.css',
]

todo_include_todos = True

def add_page_class(app, pagename, templatename, context, doctree):
    from sphinx.builders.html._assets import _CascadingStyleSheet
    context['css_files'] += [_CascadingStyleSheet(f'_static/{pagename}.css')]

def setup(app):
    # Register a sphinx.ext.autodoc.between listener to ignore everything
    # between lines that contain the word IGNORE
    app.connect(
        'autodoc-process-docstring',
        between('^.*[*]{79}.*$', exclude=True)
    )
    app.connect('html-page-context', add_page_class)
    return app
