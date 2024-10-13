from datetime import datetime
import sys
import os
from pathlib import Path
from sphinx.ext.autodoc import between
import shutil
import django

sys.path.append(str(Path(__file__).parent.parent / 'tests'))
sys.path.append(str(Path(__file__).parent.parent / 'examples'))
sys.path.append(str(Path(__file__).parent / 'ext'))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'tests.settings.base')
django.setup()

import django_typer
from literalinclude import ExtendedLiteralInclude

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

project = 'django-typer'
copyright = f'2023-{datetime.now().year}, Brian Kohan'
author = 'Brian Kohan'

# The full version, including alpha/beta/rc tags
release = django_typer.__version__


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.todo',
    'sphinxcontrib.typer',
    'sphinx_tabs.tabs'
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
# html_theme = 'sphinx_rtd_theme'
html_theme = 'furo'
html_theme_options = {
    "source_repository": "https://github.com/django-commons/django-typer/",
    "source_branch": "main",
    "source_directory": "doc/source",
}
html_title = f"{project} {release}"

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named "default.css" will overwrite the builtin "default.css".
html_static_path = ['_static']
html_css_files = ['style.css']

todo_include_todos = True

latex_engine = "xelatex"

suppress_warnings = ['app.add_directive']

linkcheck_ignore = [
    r'https://github.com/django/django/blob/main/django/core/management/__init__.py#L278',  # Ignore exact match
]

def setup(app):
    # Register a sphinx.ext.autodoc.between listener to ignore everything
    # between lines that contain the word IGNORE
    app.connect(
        'autodoc-process-docstring',
        between('^.*[*]{79}.*$', exclude=True)
    )
    # app.connect('html-page-context', add_page_class)

    app.add_directive("literalinclude", ExtendedLiteralInclude)
    
    # https://sphinxcontrib-typer.readthedocs.io/en/latest/howto.html#build-to-multiple-formats
    if Path(app.doctreedir).exists():
        shutil.rmtree(app.doctreedir)
    return app
