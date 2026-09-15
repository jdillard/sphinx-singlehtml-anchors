"""Sphinx configuration for the live singlehtml anchor demonstration."""

from __future__ import annotations

import os

from sphinx_singlehtml_anchors import __version__

project = "sphinx-singlehtml-anchors"
copyright = "2026, Jared Dillard"
author = "Jared Dillard"
release = __version__

# Build the fixed site by default. The comparison build omits the extension.
_anchors_demo = os.environ.get("SINGLEHTML_ANCHORS_DEMO", "1").lower() not in {
    "0",
    "false",
    "no",
    "off",
}

extensions = ["sphinx.ext.autosectionlabel"]
if _anchors_demo:
    extensions.append("sphinx_singlehtml_anchors")
    tags.add("with_extension")  # noqa: F821  # Sphinx-injected name
else:
    tags.add("without_extension")  # noqa: F821  # Sphinx-injected name

autosectionlabel_prefix_document = True

root_doc = "index"
exclude_patterns = ["_build", "Thumbs.db", ".DS_Store"]

html_theme = "furo"
html_title = (
    "sphinx-singlehtml-anchors"
    if _anchors_demo
    else "sphinx-singlehtml-anchors (without the extension)"
)
