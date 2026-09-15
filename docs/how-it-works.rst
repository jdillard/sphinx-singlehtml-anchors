How it works
============

Sphinx parses every source file as a separate document. Generated target IDs
are therefore unique within each source document, but the ``singlehtml``
builder later merges all those documents into one HTML page. Common headings
such as ``Overview`` and per-document generated IDs such as ``id1`` can then
occur more than once on that page.

The extension qualifies targets after the documents have been merged, while
their source-document boundaries are still available. Conceptually, the
combined targets change from:

.. code-block:: text

   overview
   id1
   overview
   id1

to:

.. code-block:: text

   document-first-guide--overview
   document-first-guide--id1
   document-second-guide--overview
   document-second-guide--id1

It also rewrites every matching reference, including section links, footnote
backreferences, local and global toctrees, figure numbering, and inventory
locations. Each internal link consequently contains one fragment that matches
one target on the combined page.

Compatibility
-------------

The extension supports released Sphinx versions from 8.1 through 9.x across
both ``SingleFileHTMLBuilder.fix_refuris()`` lifecycle behaviors:

* Sphinx 8.1.x, where Sphinx calls ``fix_refuris()``
* Sphinx 8.2.x through 9.x, where the extension supplies the omitted calls
* Sphinx versions containing the restoration proposed by
  `sphinx-doc/sphinx#14241
  <https://github.com/sphinx-doc/sphinx/pull/14241>`_
