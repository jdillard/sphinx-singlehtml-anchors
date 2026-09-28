Double-hyphen delimiter example
===============================

The ``--`` sequence is one fixed separator, not two ``-`` separators with an
empty value between them. Browsers treat the complete fragment as an opaque
identifier, and the extension does not recover document and target names by
splitting a qualified ID.

This document's name deliberately contains ``--``. The explicit label below
is also spelled with ``--``, although Sphinx normalizes its generated HTML ID
to ``separator-target``. The resulting qualified fragment still contains the
separator sequence within the document component and at the document/target
boundary. Future rewriting code must therefore retain the original
document-to-target mapping rather than parse the combined string.

.. _separator--target:

Target containing double hyphens
--------------------------------

Follow :ref:`this link back to the double-hyphen target
<separator--target>`.
