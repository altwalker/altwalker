# Configuration file for the Sphinx documentation builder.
#
# This file only contains a selection of the most common options. For a full
# list see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Path setup --------------------------------------------------------------

# If extensions (or modules to document with autodoc) are in another directory,
# add these directories to sys.path here. If the directory is relative to the
# documentation root, use os.path.abspath to make it absolute, like shown here.

import os
import sys

sys.path.insert(0, os.path.abspath('.'))


from altwalker.__version__ import VERSION


# -- Project information -----------------------------------------------------

project = 'AltWalker'
copyright = '2023, Altom Consulting'
author = 'Altom Consulting'

# The short X.Y version
version = VERSION

# The full version, including alpha/beta/rc tags
release = VERSION


# -- General configuration ---------------------------------------------------

# Add any Sphinx extension module names here, as strings. They can be
# extensions coming with Sphinx (named 'sphinx.ext.*') or your custom
# ones.
extensions = [
    'sphinx.ext.autodoc',
    'sphinx.ext.napoleon',
    'sphinx.ext.intersphinx',
    'sphinx.ext.autosectionlabel',
    'sphinx_copybutton',
    'sphinx_inline_tabs',
    'sphinx_click.ext',
    'sphinxcontrib.programoutput'
]

# Add any paths that contain templates here, relative to this directory.
templates_path = ['_templates']

# The suffix(es) of source filenames.
# You can specify multiple suffix as a list of string:
source_suffix = {
    '.rst': 'restructuredtext',
}

# List of patterns, relative to source directory, that match files and
# directories to ignore when looking for source files.
# This pattern also affects html_static_path and html_extra_path.
exclude_patterns = [
    '_build',
    '.DS_Store'
    'Thumbs.db',
]


# -- Options for HTML output -------------------------------------------------

# The theme to use for HTML and HTML Help pages.  See the documentation for
# a list of builtin themes.
html_theme = 'furo'

# If given, this must be the name of an image file (path relative to the configuration
# directory) that is the favicon of the docs. Modern browsers use this as the icon for
# tabs, windows and bookmarks. It should be a Windows-style icon file (.ico), which is
# 16x16 or 32x32 pixels large.
html_favicon = '_static/img/favicon.svg'

# If given, this must be the name of an image file (path relative to the configuration
# directory) that is the logo of the docs. It is placed at the top of the sidebar;
# its width should therefore not exceed 200 pixels.
html_logo = '_static/img/logo.svg'

# Add any paths that contain custom static files (such as style sheets) here,
# relative to this directory. They are copied after the builtin static files,
# so a file named 'default.css' will overwrite the builtin 'default.css'.
html_static_path = ['_static']

# These paths are either relative to html_static_path
# or fully qualified paths (eg. https://...)
html_css_files = [
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css',
    'https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css',
    'css/custom.css',
]

html_theme_options = {
    'sidebar_hide_name': True,
    'navigation_with_keys': True,
    'top_of_page_button': 'edit',
    'source_repository': 'https://github.com/altwalker/altwalker',
    'source_branch': 'main',
    'source_directory': '/docs/source/',
    'light_css_variables': {
        'color-brand-primary': '#166534',
        'color-brand-content': '#166534',
    },
    'dark_css_variables': {
        'color-brand-primary': '#16a34a',
        'color-brand-content': '#16a34a',
    },
    'footer_icons': [
        {
            'name': 'Gitter',
            'url': 'https://gitter.im/altwalker/community',
            'html': '',
            'class': 'mr-2 fa-brands fa-solid fa-gitter fa-lg',
        },
        {
            'name': 'GitHub',
            'url': 'https://github.com/altwalker/altwalker',
            'html': '',
            'class': 'fa-brands fa-solid fa-github fa-lg',
        }
    ]
}

# -- Options for InterSphinx -------------------------------------------------

# To add links to modules and objects in the Python standard library
# documentation.
intersphinx_mapping = {'python': ('https://docs.python.org/3', None)}


# -- Options for Autosection Label

# True to prefix each section label with the name of the document it is in, followed by a colon.
autosectionlabel_prefix_document = True
