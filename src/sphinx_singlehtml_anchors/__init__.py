"""Document-qualified anchors for Sphinx singlehtml builds."""

from __future__ import annotations

from typing import TYPE_CHECKING

from sphinx_singlehtml_anchors.builder import DocumentQualifiedSingleHTMLBuilder

if TYPE_CHECKING:
    from sphinx.application import Sphinx
    from sphinx.util.typing import ExtensionMetadata

__version__ = "0.1.0"


def setup(app: Sphinx) -> ExtensionMetadata:
    """Install the experimental replacement for Sphinx's singlehtml builder."""
    app.add_builder(DocumentQualifiedSingleHTMLBuilder, override=True)
    return {
        "version": __version__,
        "parallel_read_safe": True,
        "parallel_write_safe": True,
    }
