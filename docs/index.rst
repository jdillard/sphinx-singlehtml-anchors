sphinx-singlehtml-anchors
=========================

``sphinx-singlehtml-anchors`` gives every target in Sphinx ``singlehtml``
output a document-qualified ID. This prevents sections, footnotes, and other
targets from different source documents from receiving the same HTML ID.

This site is built as **single-page HTML** on purpose. The two guides below
contain sections with the same names and independently numbered automatic
footnotes, reproducing the collisions described in
`sphinx-doc/sphinx#4814 <https://github.com/sphinx-doc/sphinx/issues/4814>`_.

.. only:: with_extension

   .. note::

      This build uses the extension. Compare it with the
      `same docs built by Sphinx without the extension
      <without-extension/index.html>`__.

.. only:: without_extension

   .. warning::

      This comparison build does **not** use the extension. Its repeated
      section and footnote IDs demonstrate the original problem. Compare it
      with the `fixed build <../index.html>`__.

Using the extension
-------------------

Install the package and enable it in ``conf.py``:

.. code-block:: python

   extensions = [
       "sphinx_singlehtml_anchors",
   ]

Then build the documentation with Sphinx's ``singlehtml`` builder. Other
builders, including regular multi-page HTML, retain their normal target format.

How it works
------------

That is all the configuration required. The rest of this page demonstrates the
generated targets and explains implementation details.

Target format and live examples
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

In a ``singlehtml`` build, Sphinx creates an anchor for each source document.
The extension leaves that document-level anchor unchanged:

.. code-block:: text

   #document-{docname}

For targets within the document, the extension appends the original target ID
using ``--``. This makes otherwise identical target IDs unique after Sphinx
merges the source documents into one page:

.. code-block:: text

   #document-{docname}--{target-id}

.. note:: See :ref:`separator-choice` for the decision criteria, alternatives
   such as ``#``, ``:``, and ``.``, and the gotchas associated with each.

To see these qualified targets in action, follow each link and watch both the
destination and the fragment in the browser address bar:

* :ref:`Overview in the first guide <first-guide:overview>`
* :ref:`Overview in the second guide <second-guide:overview>`
* :ref:`Details in the first guide <first-guide:details>`
* :ref:`Details in the second guide <second-guide:details>`

.. only:: with_extension

   Although the visible section names repeat, each link resolves to one
   target. The fragments include the source document, for example
   ``#document-first-guide--overview`` and
   ``#document-second-guide--overview``.

.. only:: without_extension

   The combined page contains duplicate IDs such as ``overview`` and
   ``id1``. A browser can therefore select the first matching target instead
   of the target from the intended source document, and generated links
   cannot address every occurrence reliably.

The automatic footnote links in both guides exercise the same behavior with
generated IDs.

Source paths are also preserved in Sphinx docnames. The example document at
``guide/chapter.rst`` therefore has the docname ``guide/chapter``. Follow
:ref:`its Purpose section <guide/chapter:purpose>` to see the forward slash in
``#document-guide/chapter--purpose``.

Implementation details
~~~~~~~~~~~~~~~~~~~~~~

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

.. _qualified-id-name-examples:

How source names appear in qualified IDs
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

The extension does not normalize docnames or target IDs. It combines the
docname and the target ID that Sphinx has already assigned. Those inputs
follow different naming rules, which is why some examples below retain
punctuation while another is normalized. Each link is followed by the
fragment generated in this ``singlehtml`` build.

Document name with ``__``
   :doc:`The underscore example <underscore__references>` keeps its source
   docname: ``#document-underscore__references``.

Document name with ``--``
   :doc:`The delimiter example <delimiter--examples>` also keeps its source
   docname: ``#document-delimiter--examples``.

Document in a subfolder
   The source path ``guide/chapter.rst`` has the docname ``guide/chapter``.
   :ref:`Its Purpose section <guide/chapter:purpose>` therefore keeps the
   forward slash in
   ``#document-guide/chapter--purpose``.

.. _standard-label-normalization-example:

Standard label
   The source label ``separator--target`` is normalized by Docutils, so
   :ref:`its reference <separator--target>` resolves to
   ``#document-delimiter--examples--separator-target``. Standard label and
   section IDs normalize underscores and punctuation runs to a single hyphen.

Python function
   :py:func:`function_name` preserves its underscore in
   ``#document-underscore__references--function_name``.

Python dunder method
   :py:meth:`Widget.__init__` preserves its qualified Python name in
   ``#document-underscore__references--Widget.__init__``.

Python class containing ``__``
   :py:class:`Payload__Envelope` preserves both underscores in
   ``#document-underscore__references--Payload__Envelope``.

.. _separator-choice:

Separator choice and alternatives
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

HTML provides one flat ID namespace per page, so ``singlehtml`` must encode
the pair ``(source document, original target ID)`` as one ID. The current,
experimental format is:

.. code-block:: text

   document-{docname}--{target-id}

The ``--`` sequence was chosen because it is readable, needs no URL encoding,
and has no special meaning within a CSS identifier. It is also uncommon in IDs
generated by Docutils, which normalizes punctuation runs in standard labels
and section IDs to one hyphen, as shown in :ref:`the standard-label example
<standard-label-normalization-example>`. Individual docnames or target IDs
can still require CSS escaping; ``--`` merely avoids adding that requirement
to every qualified ID.

The main alternatives have tradeoffs:

Literal ``#`` inside the ID
   This introduces a URL fragment and must be referenced using an encoded
   ``%23``. URL tooling, validators, CSS selectors, JavaScript, and inventory
   consumers must all preserve the distinction between the fragment delimiter
   and the encoded character.

Colon (``:``) or period (``.``)
   In a CSS selector, a colon introduces a pseudo-class and a period introduces
   a class, so either separator must be escaped.

Underscore
   Python identifiers make ``_`` and ``__`` especially common. See
   :ref:`qualified-id-name-examples` for examples.

.. _collision-handling:

Collision handling
^^^^^^^^^^^^^^^^^^

Collisions should be rare, but docnames, custom domains, and extensions are
not guaranteed to exclude ``--``. For example, ``document-a--b--c`` could
represent either ``(a--b, c)`` or ``(a, b--c)``. The retained source-to-target
mapping avoids having to choose an interpretation.

If both pairs actually occur, the extension emits a
``[singlehtml.target_collision]`` warning and assigns each affected source
target a deterministic fallback ID. The fallback appends ``--`` and the first
16 hexadecimal characters of a SHA-256 digest of the docname, a null
separator, and the original target ID. For the example above, the two fallback
IDs are:

.. code-block:: text

   document-a--b--c--284eb05e86de2556
   document-a--b--c--f125c2f6343f3b8e

If a generated fallback is already in use, a numeric suffix such as ``-2`` is
added. The rewritten links and inventory entries use the selected fallback
ID, so the output remains unique and the build normally completes.

Repeating the same original ID within one source document is a different
ambiguity: references contain no information that can distinguish the
occurrences. The extension emits ``[singlehtml.duplicate_target]``, keeps the
first occurrence's qualified ID, removes that ID from later nodes, and
resolves references to the first occurrence.

.. toctree::
   :maxdepth: 2
   :numbered:

   first-guide
   second-guide
   guide/chapter
   underscore__references
   delimiter--examples
