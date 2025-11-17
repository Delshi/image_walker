import os
import sys

sys.path.insert(0, os.path.abspath("../.."))
project = "ImageWalker"
copyright = "2025, Delshi"
author = "Delman Delshi"

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.napoleon",
    "sphinx.ext.viewcode",
    "sphinx.ext.todo",
    "sphinx_autodoc_typehints",
    "sphinx.ext.autosummary",
]

# autosummary_generate = True
# autosummary_imported_members = True

autodoc_default_options = {
    "members": True,
    "member-order": "bysource",
    "special-members": "__init__",
    "undoc-members": True,
    "show-inheritance": True,
    "private-members": True,
}

autodoc_typehints = "description"

templates_path = ["_templates"]

napoleon_google_docstring = True
napoleon_numpy_docstring = False
napoleon_include_init_with_doc = True
napoleon_include_private_with_doc = True
napoleon_include_special_with_doc = True

html_theme = "sphinx_rtd_theme"

html_theme_options = {
    "collapse_navigation": False,
    "sticky_navigation": True,
    "navigation_depth": 4,
    "includehidden": True,
    "titles_only": False,
    # "display_version": True,
}


def setup(app):
    app.add_css_file("custom.css")


add_module_names = False
html_show_sourcelink = False
